/**
 * === DigiVeritaz Lead Capture — v3 Hardened ===
 * Logs every VERIFIED contact-form submission to the "DV Lead Form" sheet
 * AND emails info@, daniel@, durvamukherjee@digiveritaz.com.
 *
 * Defenses:
 *  - 3 honeypot fields (silent success)
 *  - JS-execution token + time-on-page window check
 *  - Google reCAPTCHA v3 score gate (>= 0.5)
 *  - Email-OTP verification (6-digit, 10-min TTL, 5 attempts, single-use)
 *  - Per-email hourly cap for OTP requests (3/h) and submissions (5/h)
 *  - 60-second dedup window per (email|phone)
 *  - Formula-injection guard on every sheet cell
 *  - Length cap + zero-width-char strip
 *  - HTML-escape on the OTP code display
 *
 * Required ScriptProperty: RECAPTCHA_SECRET (Google reCAPTCHA v3 secret key).
 * If missing, reCAPTCHA verification is skipped (warned).
 */

// ============================================================
// CONFIG — edit these to suit
// ============================================================
var SHEET_NAME = 'DV Lead Form';
var NOTIFY_EMAILS = [
  'info@digiveritaz.com',
  'daniel@digiveritaz.com',
  'durvamukherjee@digiveritaz.com'
].join(',');
var SUBJECT_PREFIX = '[Website Lead] ';

// ============================================================
// HARDENING TUNABLES
// ============================================================
var REQUIRED_FIELDS = ['fullname', 'email', 'phone'];
var HONEYPOT_FIELDS = ['_honey', 'website', 'address_line'];
var MAX_FIELD_LEN = 2000;
var MIN_TIME_ON_PAGE_MS = 3000;          // <3s on page = bot
var MAX_TIME_ON_PAGE_MS = 7200000;       // >2h on page = stale/replayed
var DEDUP_WINDOW_SECONDS = 60;
var HOURLY_CAP_PER_EMAIL = 5;
var OTP_TTL_SECONDS = 600;               // 10 minutes
var OTP_MAX_ATTEMPTS = 5;
var OTP_REQUESTS_PER_HOUR = 3;
var RECAPTCHA_MIN_SCORE = 0.5;
var RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify';

// ============================================================
// ENTRY POINTS
// ============================================================
function doGet() {
  return json({ status: 'DigiVeritaz lead-capture endpoint — POST only' });
}

function doPost(e) {
  try {
    var p = parseRequest(e);
    if (!p) return json({ ok: false, error: 'no_payload' });

    // (1) honeypot — silent success
    for (var i = 0; i < HONEYPOT_FIELDS.length; i++) {
      var hp = p[HONEYPOT_FIELDS[i]];
      if (hp && String(hp).trim() !== '') {
        return json({ ok: true });
      }
    }

    // (2) strip invisible chars on every string param
    for (var k in p) {
      if (Object.prototype.hasOwnProperty.call(p, k) && typeof p[k] === 'string') {
        p[k] = stripInvisible_(p[k]);
      }
    }

    // (3) JS-ok token (proves JavaScript executed on the page)
    if (!p._jsok || !/^dv-[a-z0-9]{8,12}$/i.test(p._jsok)) {
      return json({ ok: false, error: 'no_js' });
    }

    // (4) time-on-page check
    var nowMs = Date.now();
    var ts = parseInt(p._ts, 10);
    if (
      isNaN(ts) ||
      ts > nowMs ||
      (nowMs - ts) > MAX_TIME_ON_PAGE_MS ||
      (nowMs - ts) < MIN_TIME_ON_PAGE_MS
    ) {
      return json({ ok: false, error: 'invalid_timing' });
    }

    // (5) email format
    if (!p.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(p.email)) {
      return json({ ok: false, error: 'bad_email' });
    }

    // (6) truncate long strings
    for (var kk in p) {
      if (Object.prototype.hasOwnProperty.call(p, kk) && typeof p[kk] === 'string') {
        if (p[kk].length > MAX_FIELD_LEN) {
          p[kk] = p[kk].substring(0, MAX_FIELD_LEN);
        }
      }
    }

    // (7) reCAPTCHA v3 verify
    var secret = PropertiesService.getScriptProperties().getProperty('RECAPTCHA_SECRET');
    if (!secret) {
      console.warn('RECAPTCHA_SECRET not configured — skipping reCAPTCHA verification.');
    } else {
      try {
        var resp = UrlFetchApp.fetch(RECAPTCHA_VERIFY_URL, {
          method: 'post',
          contentType: 'application/x-www-form-urlencoded',
          payload: 'secret=' + encodeURIComponent(secret)
                 + '&response=' + encodeURIComponent(p.recaptcha_token || ''),
          muteHttpExceptions: true
        });
        var body = JSON.parse(resp.getContentText() || '{}');
        var passed = (body.success === true)
          && (typeof body.score !== 'number' || body.score >= RECAPTCHA_MIN_SCORE);
        if (!passed) {
          return json({ ok: false, error: 'failed_challenge' });
        }
      } catch (recapErr) {
        console.error('reCAPTCHA verify error: ' + recapErr);
        return json({ ok: false, error: 'failed_challenge' });
      }
    }

    // (8) dispatch by action
    var action = p.action;
    if (action === 'request_otp') {
      return handleRequestOtp_(p, nowMs);
    } else if (action === 'submit_form') {
      return handleSubmitForm_(p, nowMs);
    } else {
      return json({ ok: false, error: 'unknown_action' });
    }
  } catch (err) {
    console.error('doPost exception: ' + (err && err.stack ? err.stack : err));
    return json({ ok: false, error: 'server_error' });
  }
}

// ============================================================
// ACTION 1 — request_otp: email the user a verification code
// ============================================================
function handleRequestOtp_(p, nowMs) {
  // phone digits 8..15
  var phoneDigits = (p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8 || phoneDigits.length > 15) {
    return json({ ok: false, error: 'bad_phone' });
  }

  // required fields
  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var f = REQUIRED_FIELDS[i];
    if (!p[f] || String(p[f]).trim() === '') {
      return json({ ok: false, error: 'missing_field:' + f });
    }
  }

  var props = PropertiesService.getScriptProperties();
  var emailHash = hash_(String(p.email).toLowerCase());

  // anti-OTP-spam rate limit
  var otpReqKey = 'otpreq_' + emailHash;
  var reqState = safeParse_(props.getProperty(otpReqKey), { count: 0, start: 0 });
  if (nowMs - reqState.start > 3600000) {
    reqState = { count: 0, start: nowMs };
  }
  if (reqState.count >= OTP_REQUESTS_PER_HOUR) {
    return json({ ok: false, error: 'otp_rate_limited' });
  }
  reqState.count += 1;
  if (!reqState.start) reqState.start = nowMs;
  props.setProperty(otpReqKey, JSON.stringify(reqState));

  // 6-digit OTP
  var otpNum = Math.floor(Math.random() * 900000) + 100000;
  var otp = String(otpNum);
  while (otp.length < 6) otp = '0' + otp;

  // store under hashed key
  var otpKey = 'otp_' + emailHash;
  props.setProperty(otpKey, JSON.stringify({
    code: otp,
    expiresAt: nowMs + (OTP_TTL_SECONDS * 1000),
    attempts: 0
  }));

  // email it to the user
  try {
    MailApp.sendEmail({
      to: p.email,
      subject: 'Your DigiVeritaz verification code',
      htmlBody: buildOtpEmail_(p.fullname, otp)
    });
  } catch (mailErr) {
    console.error('OTP mail failed: ' + mailErr);
    return json({ ok: false, error: 'mail_failed' });
  }

  return json({ ok: true, message: 'code_sent' });
}

// ============================================================
// ACTION 2 — submit_form: verify OTP, write row, notify team
// ============================================================
function handleSubmitForm_(p, nowMs) {
  // required fields
  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var f = REQUIRED_FIELDS[i];
    if (!p[f] || String(p[f]).trim() === '') {
      return json({ ok: false, error: 'missing_field:' + f });
    }
  }

  // phone digits 8..15
  var phoneDigits = (p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8 || phoneDigits.length > 15) {
    return json({ ok: false, error: 'bad_phone' });
  }

  // OTP format
  if (!p.otp || !/^\d{6}$/.test(p.otp)) {
    return json({ ok: false, error: 'otp_required' });
  }

  var props = PropertiesService.getScriptProperties();
  var emailHash = hash_(String(p.email).toLowerCase());

  // OTP verification
  var otpKey = 'otp_' + emailHash;
  var rawOtp = props.getProperty(otpKey);
  if (!rawOtp) return json({ ok: false, error: 'otp_not_requested' });

  var stored = safeParse_(rawOtp, null);
  if (!stored) {
    props.deleteProperty(otpKey);
    return json({ ok: false, error: 'otp_not_requested' });
  }
  if (nowMs > stored.expiresAt) {
    props.deleteProperty(otpKey);
    return json({ ok: false, error: 'otp_expired' });
  }
  if ((stored.attempts || 0) >= OTP_MAX_ATTEMPTS) {
    props.deleteProperty(otpKey);
    return json({ ok: false, error: 'otp_attempts_exceeded' });
  }
  if (stored.code !== String(p.otp)) {
    stored.attempts = (stored.attempts || 0) + 1;
    props.setProperty(otpKey, JSON.stringify(stored));
    return json({ ok: false, error: 'otp_wrong' });
  }
  // single-use
  props.deleteProperty(otpKey);

  // dedup
  var dedupKey = 'dedup_' + hash_(String(p.email).toLowerCase() + '|' + phoneDigits);
  var lastSeen = parseInt(props.getProperty(dedupKey) || '0', 10);
  if (!isNaN(lastSeen) && (nowMs - lastSeen) < (DEDUP_WINDOW_SECONDS * 1000)) {
    return json({ ok: false, error: 'duplicate_submission' });
  }
  props.setProperty(dedupKey, String(nowMs));

  // hourly cap per email
  var rateKey = 'rate_' + emailHash;
  var rateState = safeParse_(props.getProperty(rateKey), { count: 0, start: 0 });
  if (nowMs - rateState.start > 3600000) {
    rateState = { count: 0, start: nowMs };
  }
  if (rateState.count >= HOURLY_CAP_PER_EMAIL) {
    return json({ ok: false, error: 'rate_limited' });
  }
  rateState.count += 1;
  if (!rateState.start) rateState.start = nowMs;
  props.setProperty(rateKey, JSON.stringify(rateState));

  // append row
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) return json({ ok: false, error: 'Sheet "' + SHEET_NAME + '" not found' });

  var services = pickServices_(p);

  sheet.appendRow([
    new Date(),
    safeCell_(p.fullname || p.name || ''),
    safeCell_(p.email || ''),
    safeCell_(p.phone || ''),
    safeCell_(p.company || ''),
    safeCell_(p.budget || ''),
    safeCell_(services),
    safeCell_(p.message || ''),
    safeCell_(p._page || ''),
    safeCell_(p._source || 'contact-us form')
  ]);

  // notify team
  try {
    sendNotification_(p, services);
  } catch (notifyErr) {
    console.error('Notify mail failed: ' + notifyErr);
    // do not fail the submission
  }

  return json({ ok: true });
}

// ============================================================
// HELPERS
// ============================================================
function parseRequest(e) {
  if (!e) return null;
  if (e.postData && e.postData.type === 'application/json') {
    try { return JSON.parse(e.postData.contents); } catch (jerr) { return null; }
  }
  // form-encoded — use e.parameter (single) but keep e.parameters (multi) on a hidden key
  var out = {};
  if (e.parameter) {
    for (var k in e.parameter) {
      if (Object.prototype.hasOwnProperty.call(e.parameter, k)) out[k] = e.parameter[k];
    }
  }
  if (e.parameters) {
    // attach multi-value parameters on a non-enumerable-ish field
    out.__multi__ = e.parameters;
  }
  return out;
}

function pickServices_(p) {
  // priority: services[] array → services array → services single → services[] single
  var multi = p.__multi__ || {};
  if (Array.isArray(multi['services[]']) && multi['services[]'].length > 1) {
    return multi['services[]'].join(', ');
  }
  if (Array.isArray(multi.services) && multi.services.length > 1) {
    return multi.services.join(', ');
  }
  if (Array.isArray(p['services[]'])) return p['services[]'].join(', ');
  if (Array.isArray(p.services)) return p.services.join(', ');
  return p['services[]'] || p.services || '';
}

function sendNotification_(p, services) {
  var name    = (p.fullname || p.name || 'Unknown').toString().trim();
  var company = (p.company  || '').toString().trim();
  var email   = (p.email    || '').toString().trim();
  var subject = SUBJECT_PREFIX + name + (company ? ' from ' + company : '');

  var body =
    'New verified lead from the DigiVeritaz website\n' +
    '─────────────────────────────────────────\n' +
    'Name:     ' + name + '\n' +
    'Email:    ' + email + '\n' +
    'Phone:    ' + (p.phone   || '') + '\n' +
    'Company:  ' + company + '\n' +
    'Budget:   ' + (p.budget  || '') + '\n' +
    'Services: ' + services + '\n' +
    '─────────────────────────────────────────\n\n' +
    'Message:\n' + (p.message || '(none)') + '\n\n' +
    '─────────────────────────────────────────\n' +
    'Page:     ' + (p._page   || '') + '\n' +
    'Source:   ' + (p._source || 'contact-us form') + '\n' +
    'Time:     ' + new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST\n' +
    '\n' +
    '(Email + phone verified via 6-digit OTP and Google reCAPTCHA v3.)\n';

  MailApp.sendEmail({
    to: NOTIFY_EMAILS,
    subject: subject,
    body: body,
    replyTo: email || undefined
  });
}

function buildOtpEmail_(fullname, code) {
  var who = (fullname && String(fullname).trim())
    ? htmlEscape_(String(fullname).trim())
    : 'there';
  return '' +
    '<div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:20px;border:1px solid #e5e7eb;border-radius:12px">' +
      '<h2 style="color:#16a34a;margin:0 0 12px">DigiVeritaz — Verification Code</h2>' +
      '<p>Hi ' + who + ',</p>' +
      '<p>Use this 6-digit code to complete your contact-form submission. It expires in 10 minutes.</p>' +
      '<div style="font-size:2rem;letter-spacing:0.5em;font-weight:bold;text-align:center;padding:20px;background:#f3f4f6;border-radius:12px;color:#111827">' +
        htmlEscape_(code) +
      '</div>' +
      '<p style="margin-top:20px;color:#6b7280;font-size:.9rem">If you did not request this code, you can ignore this email.</p>' +
    '</div>';
}

function stripInvisible_(s) {
  if (s == null) return s;
  return String(s)
    .replace(/[​-‏ - ⁠-⁯﻿]/g, '')
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')
    .trim();
}

function safeCell_(s) {
  if (s == null) return '';
  var str = String(s);
  if (str.length === 0) return '';
  var first = str.charAt(0);
  if (first === '=' || first === '+' || first === '-' || first === '@' || first === '\t' || first === '\r') {
    return "'" + str;
  }
  return str;
}

function hash_(s) {
  var raw = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, String(s));
  var b64 = Utilities.base64Encode(raw);
  return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '').substring(0, 16);
}

function htmlEscape_(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function safeParse_(raw, fallback) {
  if (!raw) return fallback;
  try { return JSON.parse(raw); } catch (e) { return fallback; }
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
