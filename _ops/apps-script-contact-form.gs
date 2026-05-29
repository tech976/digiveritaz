/**
 * DigiVeritaz Contact Form — v2 Hardened Apps Script
 * Email OTP + Google reCAPTCHA v3 + anti-abuse defenses
 */

// ============================================================
// CONSTANTS
// ============================================================
var SHEET_NAME = 'DV Lead Form';
var REQUIRED_FIELDS = ['fullname', 'email', 'phone'];
var HONEYPOT_FIELDS = ['_honey', 'website', 'address_line'];
var MAX_FIELD_LEN = 2000;
var MIN_TIME_ON_PAGE_MS = 3000;
var MAX_TIME_ON_PAGE_MS = 7200000;
var DEDUP_WINDOW_SECONDS = 60;
var HOURLY_CAP_PER_EMAIL = 5;
var OTP_TTL_SECONDS = 600;            // 10 minutes
var OTP_MAX_ATTEMPTS = 5;
var OTP_REQUESTS_PER_HOUR = 3;        // anti-OTP-spam
var RECAPTCHA_MIN_SCORE = 0.5;        // v3 score threshold
var NOTIFICATION_EMAIL = 'campaign@digiveritaz.com';
var RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify';
// ScriptProperties key for recaptcha secret: 'RECAPTCHA_SECRET'

// ============================================================
// ENTRY POINT
// ============================================================
function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : null;

    // (a) payload presence
    if (!p) return reply_({ ok: false, error: 'no_payload' });

    // (b) honeypot — silent success
    for (var i = 0; i < HONEYPOT_FIELDS.length; i++) {
      var hp = p[HONEYPOT_FIELDS[i]];
      if (hp && String(hp).trim() !== '') {
        return reply_({ ok: true });
      }
    }

    // (c) strip invisible chars on every string param
    for (var k in p) {
      if (Object.prototype.hasOwnProperty.call(p, k) && typeof p[k] === 'string') {
        p[k] = stripInvisible_(p[k]);
      }
    }

    // (d) JS-ok token
    if (!p._jsok || !/^dv-[a-z0-9]{8,12}$/i.test(p._jsok)) {
      return reply_({ ok: false, error: 'no_js' });
    }

    // (e) timing check
    var nowMs = Date.now();
    var ts = parseInt(p._ts, 10);
    if (
      isNaN(ts) ||
      ts > nowMs ||
      (nowMs - ts) > MAX_TIME_ON_PAGE_MS ||
      (nowMs - ts) < MIN_TIME_ON_PAGE_MS
    ) {
      return reply_({ ok: false, error: 'invalid_timing' });
    }

    // (f) email format
    if (!p.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(p.email)) {
      return reply_({ ok: false, error: 'bad_email' });
    }

    // (g) truncate long strings
    for (var kk in p) {
      if (Object.prototype.hasOwnProperty.call(p, kk) && typeof p[kk] === 'string') {
        if (p[kk].length > MAX_FIELD_LEN) {
          p[kk] = p[kk].substring(0, MAX_FIELD_LEN);
        }
      }
    }

    // (h) reCAPTCHA v3 verify
    var secret = PropertiesService.getScriptProperties().getProperty('RECAPTCHA_SECRET');
    if (!secret) {
      console.warn('RECAPTCHA_SECRET not configured in ScriptProperties; skipping reCAPTCHA verification.');
    } else {
      try {
        var resp = UrlFetchApp.fetch(RECAPTCHA_VERIFY_URL, {
          method: 'post',
          contentType: 'application/x-www-form-urlencoded',
          payload: 'secret=' + encodeURIComponent(secret) + '&response=' + encodeURIComponent(p.recaptcha_token || ''),
          muteHttpExceptions: true
        });
        var body = JSON.parse(resp.getContentText() || '{}');
        var passed = (body.success === true) && (typeof body.score !== 'number' || body.score >= RECAPTCHA_MIN_SCORE);
        if (!passed) {
          return reply_({ ok: false, error: 'failed_challenge' });
        }
      } catch (recapErr) {
        console.error('reCAPTCHA verify error: ' + recapErr);
        return reply_({ ok: false, error: 'failed_challenge' });
      }
    }

    // Dispatch by action
    var action = p.action;
    if (action === 'request_otp') {
      return handleRequestOtp_(p, nowMs);
    } else if (action === 'submit_form') {
      return handleSubmitForm_(p, nowMs);
    } else {
      return reply_({ ok: false, error: 'unknown_action' });
    }
  } catch (err) {
    console.error('doPost exception: ' + (err && err.stack ? err.stack : err));
    return reply_({ ok: false, error: 'server_error' });
  }
}

// ============================================================
// ACTION 1: request_otp
// ============================================================
function handleRequestOtp_(p, nowMs) {
  // 1) phone digits 8..15
  var phoneDigits = (p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8 || phoneDigits.length > 15) {
    return reply_({ ok: false, error: 'bad_phone' });
  }

  // 2) required fields
  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var f = REQUIRED_FIELDS[i];
    if (!p[f] || String(p[f]).trim() === '') {
      return reply_({ ok: false, error: 'missing_field:' + f });
    }
  }

  var props = PropertiesService.getScriptProperties();
  var emailHash = hash_(String(p.email).toLowerCase());

  // 3) OTP request rate-limit per email per hour
  var otpReqKey = 'otpreq_' + emailHash;
  var rawReq = props.getProperty(otpReqKey);
  var reqState = { count: 0, start: 0 };
  if (rawReq) {
    try { reqState = JSON.parse(rawReq); } catch (e2) { reqState = { count: 0, start: 0 }; }
  }
  if (nowMs - reqState.start > 3600000) {
    reqState = { count: 0, start: nowMs };
  }
  if (reqState.count >= OTP_REQUESTS_PER_HOUR) {
    return reply_({ ok: false, error: 'otp_rate_limited' });
  }
  reqState.count += 1;
  if (!reqState.start) reqState.start = nowMs;
  props.setProperty(otpReqKey, JSON.stringify(reqState));

  // 4) generate 6-digit OTP
  var otpNum = Math.floor(Math.random() * 900000) + 100000;
  var otp = String(otpNum);
  while (otp.length < 6) { otp = '0' + otp; }

  // 5) store OTP
  var otpKey = 'otp_' + emailHash;
  var otpRecord = {
    code: otp,
    expiresAt: nowMs + (OTP_TTL_SECONDS * 1000),
    attempts: 0
  };
  props.setProperty(otpKey, JSON.stringify(otpRecord));

  // 6) email OTP to user
  try {
    MailApp.sendEmail({
      to: p.email,
      subject: 'Your DigiVeritaz verification code',
      htmlBody: buildOtpEmail_(p.fullname, otp)
    });
  } catch (mailErr) {
    console.error('OTP mail failed: ' + (mailErr && mailErr.stack ? mailErr.stack : mailErr));
    return reply_({ ok: false, error: 'mail_failed' });
  }

  // 7) success
  return reply_({ ok: true, message: 'code_sent' });
}

// ============================================================
// ACTION 2: submit_form
// ============================================================
function handleSubmitForm_(p, nowMs) {
  // 1) required fields
  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var f = REQUIRED_FIELDS[i];
    if (!p[f] || String(p[f]).trim() === '') {
      return reply_({ ok: false, error: 'missing_field:' + f });
    }
  }

  // 2) phone digits 8..15
  var phoneDigits = (p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8 || phoneDigits.length > 15) {
    return reply_({ ok: false, error: 'bad_phone' });
  }

  // 3) OTP format
  if (!p.otp || !/^\d{6}$/.test(p.otp)) {
    return reply_({ ok: false, error: 'otp_required' });
  }

  var props = PropertiesService.getScriptProperties();
  var emailHash = hash_(String(p.email).toLowerCase());

  // 4) OTP verification
  var otpKey = 'otp_' + emailHash;
  var rawOtp = props.getProperty(otpKey);
  if (!rawOtp) {
    return reply_({ ok: false, error: 'otp_not_requested' });
  }
  var stored;
  try {
    stored = JSON.parse(rawOtp);
  } catch (parseErr) {
    props.deleteProperty(otpKey);
    return reply_({ ok: false, error: 'otp_not_requested' });
  }
  if (nowMs > stored.expiresAt) {
    props.deleteProperty(otpKey);
    return reply_({ ok: false, error: 'otp_expired' });
  }
  if ((stored.attempts || 0) >= OTP_MAX_ATTEMPTS) {
    props.deleteProperty(otpKey);
    return reply_({ ok: false, error: 'otp_attempts_exceeded' });
  }
  if (stored.code !== String(p.otp)) {
    stored.attempts = (stored.attempts || 0) + 1;
    props.setProperty(otpKey, JSON.stringify(stored));
    return reply_({ ok: false, error: 'otp_wrong' });
  }
  // matched — single-use
  props.deleteProperty(otpKey);

  // 5) dedup + per-email hourly rate-limit
  var dedupKey = 'dedup_' + hash_(String(p.email).toLowerCase() + '|' + phoneDigits);
  var lastSeen = props.getProperty(dedupKey);
  if (lastSeen) {
    var lastTs = parseInt(lastSeen, 10);
    if (!isNaN(lastTs) && (nowMs - lastTs) < (DEDUP_WINDOW_SECONDS * 1000)) {
      return reply_({ ok: false, error: 'duplicate_submission' });
    }
  }
  props.setProperty(dedupKey, String(nowMs));

  var rateKey = 'rate_' + emailHash;
  var rawRate = props.getProperty(rateKey);
  var rateState = { count: 0, start: 0 };
  if (rawRate) {
    try { rateState = JSON.parse(rawRate); } catch (e3) { rateState = { count: 0, start: 0 }; }
  }
  if (nowMs - rateState.start > 3600000) {
    rateState = { count: 0, start: nowMs };
  }
  if (rateState.count >= HOURLY_CAP_PER_EMAIL) {
    return reply_({ ok: false, error: 'rate_limited' });
  }
  rateState.count += 1;
  if (!rateState.start) rateState.start = nowMs;
  props.setProperty(rateKey, JSON.stringify(rateState));

  // 6) safeCell guard + 7) append to sheet
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow([
      'Timestamp', 'Full Name', 'Email', 'Phone',
      'Company', 'Services', 'Message', 'Source'
    ]);
  }

  var fullname  = safeCell_(p.fullname || '');
  var email     = safeCell_(p.email || '');
  var phone     = safeCell_(p.phone || '');
  var company   = safeCell_(p.company || '');
  var services  = safeCell_(p.services || '');
  var message   = safeCell_(p.message || '');
  var source    = safeCell_(p.source || '');

  sheet.appendRow([
    new Date(),
    fullname,
    email,
    phone,
    company,
    services,
    message,
    source
  ]);

  // 8) notification email to team
  try {
    MailApp.sendEmail({
      to: NOTIFICATION_EMAIL,
      subject: 'New DV Lead — ' + (p.fullname || 'Unknown'),
      htmlBody: buildEmailNotify_(p, services)
    });
  } catch (notifyErr) {
    console.error('Notify mail failed: ' + (notifyErr && notifyErr.stack ? notifyErr.stack : notifyErr));
    // Do not fail submission if notification fails
  }

  // 9) success
  return reply_({ ok: true });
}

// ============================================================
// HELPERS
// ============================================================
function reply_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function stripInvisible_(s) {
  if (s == null) return s;
  // Remove zero-width and BOM-like chars, control chars (except \n, \r, \t)
  return String(s)
    .replace(/[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]/g, '')
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
  // URL-safe variant
  var safe = b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  return safe.substring(0, 16);
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

function buildEmailNotify_(p, services) {
  var rows = [
    ['Full Name', p.fullname || ''],
    ['Email',     p.email || ''],
    ['Phone',     p.phone || ''],
    ['Company',   p.company || ''],
    ['Services',  services || p.services || ''],
    ['Message',   p.message || ''],
    ['Source',    p.source || '']
  ];
  var rowsHtml = rows.map(function (r) {
    return '<tr>' +
      '<td style="padding:8px 12px;border:1px solid #e5e7eb;background:#f9fafb;font-weight:600;color:#374151">' +
        htmlEscape_(r[0]) +
      '</td>' +
      '<td style="padding:8px 12px;border:1px solid #e5e7eb;color:#111827">' +
        htmlEscape_(r[1]) +
      '</td>' +
    '</tr>';
  }).join('');

  return '' +
    '<div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto;padding:20px">' +
      '<h2 style="color:#16a34a;margin:0 0 16px">New DigiVeritaz Lead</h2>' +
      '<p style="color:#374151;margin:0 0 16px">A verified contact-form submission was received.</p>' +
      '<table style="border-collapse:collapse;width:100%;border:1px solid #e5e7eb">' +
        rowsHtml +
      '</table>' +
      '<p style="margin-top:20px;color:#6b7280;font-size:.85rem">' +
        'Submitted at ' + htmlEscape_(new Date().toString()) +
      '</p>' +
    '</div>';
}

function buildOtpEmail_(fullname, code) {
  var who = (fullname && String(fullname).trim()) ? htmlEscape_(String(fullname).trim()) : 'there';
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
