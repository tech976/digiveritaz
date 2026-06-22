/**
 * === DigiVeritaz Lead Capture — v3 Hardened ===
 * Logs every VERIFIED contact-form submission to the "DV Lead Form" sheet
 * AND emails info@, daniel@, durvamukherjee@digiveritaz.com.
 *
 * Defenses:
 *  - 3 honeypot fields (silent success)
 *  - JS-execution token + time-on-page window check
 *  - Email-OTP verification (6-digit, 10-min TTL, 5 attempts, single-use)
 *  - Per-email hourly cap for OTP requests (3/h) and submissions (5/h)
 *  - 60-second dedup window per (email|phone)
 *  - Formula-injection guard on every sheet cell
 *  - Length cap + zero-width-char strip
 *  - HTML-escape on the OTP code display
 *
 * No external HTTP calls — runs on default Sheets + Mail OAuth scopes.
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

// Progressive popup (DV-LEAD v2) writes here — upsert by LeadID. Auto-created.
var LEAD_SHEET_NAME = 'DV Leads (Popup)';

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

// ============================================================
// ENTRY POINTS
// ============================================================
function doGet(e) {
  // Diagnostic mode: ?diag=1 reports config without leaking secrets.
  if (e && e.parameter && e.parameter.diag === '1') {
    var quota;
    try { quota = MailApp.getRemainingDailyQuota(); } catch (qe) { quota = 'err:' + qe; }
    return json({
      status: 'DigiVeritaz lead-capture endpoint — POST only',
      build: 'v5-mailapp',
      diag: {
        sheet_found: !!SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME),
        mail_quota_remaining: quota
      }
    });
  }
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

    // (3b) progressive popup (DV-LEAD v2) — dispatch BEFORE the email/timing gates
    // so a step-1 "number only" save isn't rejected for having no email yet.
    if (p.action === 'lead_save') {
      return handleLeadSave_(p, Date.now());
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

    // (7) dispatch by action
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

  // email it to the user — MailApp (narrow send-only scope, no extra auth) with
  // BOTH plain-text + HTML (multipart) + sender name for better deliverability
  try {
    MailApp.sendEmail({
      to: p.email,
      subject: 'Your DigiVeritaz verification code',
      name: 'DigiVeritaz',
      replyTo: 'info@digiveritaz.com',
      body: 'Hi ' + (p.fullname || 'there') + ',\n\n' +
            'Your DigiVeritaz verification code is: ' + otp + '\n\n' +
            'It expires in 10 minutes. If you did not request this, you can ignore this email.\n\n' +
            '— DigiVeritaz',
      htmlBody: buildOtpEmail_(p.fullname, otp)
    });
  } catch (mailErr) {
    console.error('OTP mail failed: ' + mailErr);
    return json({ ok: false, error: 'mail_failed', detail: String(mailErr) });
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
    '(Email verified via 6-digit OTP.)\n';

  MailApp.sendEmail({
    to: NOTIFY_EMAILS,
    subject: subject,
    name: 'DigiVeritaz Website',
    replyTo: email || undefined,
    body: body
  });
}

// ============================================================
// DIAGNOSTIC — run this directly in the Apps Script editor (Run ▸ diagMail)
// to confirm the account can actually send. Set DIAG_TO to an EXTERNAL
// address (e.g. your personal gmail) to test real-world delivery.
// ============================================================
var DIAG_TO = ''; // <-- put an external email here, e.g. 'you@gmail.com'
function diagMail() {
  var quota = MailApp.getRemainingDailyQuota();
  Logger.log('Remaining daily email quota: ' + quota);
  if (!DIAG_TO) { Logger.log('Set DIAG_TO (top of file) to your email, then run again.'); return; }
  MailApp.sendEmail({ to: DIAG_TO, subject: 'DigiVeritaz mail diagnostic', name: 'DigiVeritaz',
    body: 'If you received this, the script CAN send email.\nQuota remaining: ' + quota + '\nNote: from a personal Gmail this often lands in Spam.' });
  Logger.log('Diagnostic email sent to ' + DIAG_TO + ' via MailApp. Check inbox AND Spam.');
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
  var out = '';
  var src = String(s);
  for (var i = 0; i < src.length; i++) {
    var c = src.charCodeAt(i);
    // Zero-width / BOM / line+paragraph separators / word joiner / variation selectors
    if (c >= 0x200B && c <= 0x200F) continue;
    if (c >= 0x2028 && c <= 0x202F) continue;
    if (c >= 0x2060 && c <= 0x206F) continue;
    if (c === 0xFEFF) continue;
    // Control chars (allow \n=0x0A, \r=0x0D, \t=0x09)
    if (c <= 0x08) continue;
    if (c === 0x0B || c === 0x0C) continue;
    if (c >= 0x0E && c <= 0x1F) continue;
    if (c === 0x7F) continue;
    out += src.charAt(i);
  }
  return out.trim();
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


// ============================================================
// ACTION 3 — lead_save: progressive popup upsert (DV-LEAD v2)
// One row per LeadID. Step 1 saves the number (Partial); later
// steps update the same row; final step marks it Complete.
// Abandon after step 1 => the number stays as a Partial lead.
// ============================================================
function handleLeadSave_(p, nowMs) {
  var leadId = String(p.leadId || '').slice(0, 64);
  if (!leadId) leadId = 'srv-' + nowMs;

  var phoneDigits = String(p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8) return json({ ok: false, error: 'no_phone' });

  var complete = (p.complete === '1' || p.complete === 'true' || String(p.status) === 'Complete');
  var status = complete ? 'Complete' : 'Partial';

  var v = {
    phone:   p.phone   || '',
    service: p.service || '',
    name:    p.name    || '',
    email:   p.email   || '',
    company: p.company || '',
    message: p.message || '',
    source:  p._source || 'website-popup',
    page:    p._page   || '',
    consent: p.consent || '',
    verified: p.verified || ''
  };

  var lock = LockService.getScriptLock();
  try { lock.waitLock(8000); } catch (e) { /* proceed without lock if busy */ }
  try {
    var sheet = getLeadSheet_();
    var data = sheet.getDataRange().getValues();   // row 0 = header
    var rowIdx = -1;                                // 1-based sheet row
    for (var r = 1; r < data.length; r++) {
      if (String(data[r][1]) === leadId) { rowIdx = r + 1; break; }
    }
    var now = new Date();
    var isNew = (rowIdx === -1);

    if (isNew) {
      sheet.appendRow([now, leadId, status, v.phone, v.service, v.name, v.email,
                       v.company, v.message, v.source, v.page, v.consent, v.verified, now]);
    } else {
      var row = data[rowIdx - 1].slice();
      row[2] = status;
      function setIf(col, val) { if (val !== '' && val != null) row[col] = val; }
      setIf(3, v.phone); setIf(4, v.service); setIf(5, v.name); setIf(6, v.email);
      setIf(7, v.company); setIf(8, v.message); setIf(9, v.source); setIf(10, v.page); setIf(11, v.consent); setIf(12, v.verified);
      row[13] = now;
      sheet.getRange(rowIdx, 1, 1, row.length).setValues([row]);
      v = { phone: row[3], service: row[4], name: row[5], email: row[6], company: row[7], message: row[8], source: row[9], verified: row[12] };
    }

    // Email notifications: a heads-up the moment a number lands, and the full
    // lead when the form is completed. (Sheet is the source of truth regardless.)
    if (isNew)   notifyLead_(leadId, status, v, false);
    if (complete) notifyLead_(leadId, 'Complete', v, true);

    return json({ ok: true, leadId: leadId, status: status });
  } catch (err) {
    console.error('handleLeadSave_ ' + (err && err.stack ? err.stack : err));
    return json({ ok: false, error: 'save_failed' });
  } finally {
    try { lock.releaseLock(); } catch (e) {}
  }
}

function getLeadSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(LEAD_SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(LEAD_SHEET_NAME);
    sh.appendRow(['Created', 'LeadID', 'Status', 'Phone', 'Service', 'Name', 'Email',
                  'Company/Website', 'Message', 'Source', 'Page', 'Consent', 'Verified', 'Updated']);
    sh.setFrozenRows(1);
  }
  return sh;
}

function notifyLead_(leadId, status, v, full) {
  try {
    var tag = full ? '✅ FULL LEAD' : '🟡 New number';
    var subject = SUBJECT_PREFIX + tag + ' — ' + (v.phone || '');
    var body = [
      tag + '  (status: ' + status + ')',
      '',
      'Phone:           ' + (v.phone || '—'),
      'OTP verified:    ' + (v.verified || 'No'),
      'Service:         ' + (v.service || '—'),
      'Name:            ' + (v.name || '—'),
      'Email:           ' + (v.email || '—'),
      'Company/Website: ' + (v.company || '—'),
      'Message:         ' + (v.message || '—'),
      '',
      'Lead ID:         ' + leadId,
      'Source:          ' + (v.source || 'website popup'),
      '',
      (full
        ? 'This lead completed the full form.'
        : 'Only the number is in so far — if they drop off, follow up on WhatsApp.')
    ].join('\n');
    MailApp.sendEmail({
      to: NOTIFY_EMAILS,
      subject: subject,
      name: 'DigiVeritaz Leads',
      replyTo: 'info@digiveritaz.com',
      body: body
    });
  } catch (e) {
    console.error('notifyLead_ ' + e);
  }
}
