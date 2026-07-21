/**
 * === DigiVeritaz Lead Capture — v8 (MailApp + CRM webhook push + CRM sheet feed + user ack) ===
 * REPO REFERENCE COPY — this is a version-control snapshot only. The LIVE script runs
 * as a Google Apps Script Web App in the DigiVeritaz Google account and must be updated
 * by pasting this into the Apps Script editor and redeploying (Manage deployments ->
 * New version, same /exec URL). Pushing this file to git does NOT deploy it.
 *
 * SECURITY: CRM_WEBHOOK_SECRET is REDACTED here so it is never committed to the repo.
 * In the live deployment, set the real secret (ideally via Project Settings -> Script
 * Properties, key CRM_WEBHOOK_SECRET), then read it below.
 *
 * Logs every submission (Partial when number is entered, Complete on submit) to the
 * "DV Lead Form" sheet, upserting by Lead ID so a lead occupies ONE row. Emails
 * info@, daniel@, durvamukherjee@, bd@digiveritaz.com — only on the Complete lead.
 * Also: (CRM) pushes each lead to the CRM webhook, and serves a read-only JSON
 * feed of the whole sheet to the CRM "Website Leads" tab.
 * (USER-ACK) sends a thank-you email to the person who submitted, on Complete only.
 */

// ============================================================
// CONFIG
// ============================================================
var SHEET_NAME = 'DV Lead Form';
var NOTIFY_EMAILS = [
  'info@digiveritaz.com',
  'daniel@digiveritaz.com',
  'durvamukherjee@digiveritaz.com',
  'bd@digiveritaz.com'
].join(',');
var SUBJECT_PREFIX = '[Website Lead] ';

// CRM — push completed leads to the CRM + serve the sheet feed (same secret for both)
var CRM_WEBHOOK_URL    = 'https://crm.digiveritaz.tech/api/website/lead';
// Redacted in the repo. In the live editor use the real value, or set a Script Property
// named CRM_WEBHOOK_SECRET and this line will pick it up automatically.
var CRM_WEBHOOK_SECRET = PropertiesService.getScriptProperties().getProperty('CRM_WEBHOOK_SECRET') || 'REDACTED_IN_REPO';

// ============================================================
// HARDENING TUNABLES
// ============================================================
var REQUIRED_FIELDS = ['fullname', 'email', 'phone'];
var HONEYPOT_FIELDS = ['_honey', 'website', 'address_line'];
var MAX_FIELD_LEN = 2000;
var MIN_TIME_ON_PAGE_MS = 3000;
var MAX_TIME_ON_PAGE_MS = 172800000;     // 48h window (widened from 2h so long-open tabs are not dropped)
var DEDUP_WINDOW_SECONDS = 60;
var HOURLY_CAP_PER_EMAIL = 5;
var OTP_TTL_SECONDS = 600;
var OTP_MAX_ATTEMPTS = 5;
var OTP_REQUESTS_PER_HOUR = 3;

// ============================================================
// ENTRY POINTS
// ============================================================
function doGet(e) {
  // CRM — live sheet feed for the "Website Leads" tab
  if (e && e.parameter && e.parameter.action === 'list') {
    if (e.parameter.secret !== CRM_WEBHOOK_SECRET) return json({ ok: false, error: 'unauthorized' });
    return json({ ok: true, rows: readAllLeadRows_() });
  }

  if (e && e.parameter && e.parameter.diag === '1') {
    var quota;
    try { quota = MailApp.getRemainingDailyQuota(); } catch (qe) { quota = 'err:' + qe; }
    return json({
      status: 'DigiVeritaz lead-capture endpoint — POST only',
      build: 'v9-utm-attribution',
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

    for (var i = 0; i < HONEYPOT_FIELDS.length; i++) {
      var hp = p[HONEYPOT_FIELDS[i]];
      if (hp && String(hp).trim() !== '') { return json({ ok: true }); }
    }

    for (var k in p) {
      if (Object.prototype.hasOwnProperty.call(p, k) && typeof p[k] === 'string') {
        p[k] = stripInvisible_(p[k]);
      }
    }

    if (!p._jsok || !/^dv-[a-z0-9]{8,12}$/i.test(p._jsok)) {
      return json({ ok: false, error: 'no_js' });
    }

    var nowMs = Date.now();
    var ts = parseInt(p._ts, 10);
    if (isNaN(ts) || ts > nowMs || (nowMs - ts) > MAX_TIME_ON_PAGE_MS || (nowMs - ts) < MIN_TIME_ON_PAGE_MS) {
      return json({ ok: false, error: 'invalid_timing' });
    }

    for (var kk in p) {
      if (Object.prototype.hasOwnProperty.call(p, kk) && typeof p[kk] === 'string') {
        if (p[kk].length > MAX_FIELD_LEN) { p[kk] = p[kk].substring(0, MAX_FIELD_LEN); }
      }
    }

    // email is validated per-action below — partial saves may not have an email yet
    var emailRe = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    var action = p.action;
    if (action === 'request_otp') {
      if (!p.email || !emailRe.test(p.email)) return json({ ok: false, error: 'bad_email' });
      return handleRequestOtp_(p, nowMs);
    } else if (action === 'submit_form') {
      if (!p.email || !emailRe.test(p.email)) return json({ ok: false, error: 'bad_email' });
      return handleSubmitForm_(p, nowMs);
    } else if (action === 'lead_save') {
      return handleLeadSave_(p, nowMs);
    } else {
      return json({ ok: false, error: 'unknown_action' });
    }
  } catch (err) {
    console.error('doPost exception: ' + (err && err.stack ? err.stack : err));
    return json({ ok: false, error: 'server_error' });
  }
}

// ============================================================
// ACTION 1 — request_otp  (legacy email-OTP fallback)
// ============================================================
function handleRequestOtp_(p, nowMs) {
  var phoneDigits = (p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8 || phoneDigits.length > 15) {
    return json({ ok: false, error: 'bad_phone' });
  }
  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var f = REQUIRED_FIELDS[i];
    if (!p[f] || String(p[f]).trim() === '') { return json({ ok: false, error: 'missing_field:' + f }); }
  }

  var props = PropertiesService.getScriptProperties();
  var emailHash = hash_(String(p.email).toLowerCase());

  var otpReqKey = 'otpreq_' + emailHash;
  var reqState = safeParse_(props.getProperty(otpReqKey), { count: 0, start: 0 });
  if (nowMs - reqState.start > 3600000) { reqState = { count: 0, start: nowMs }; }
  if (reqState.count >= OTP_REQUESTS_PER_HOUR) { return json({ ok: false, error: 'otp_rate_limited' }); }
  reqState.count += 1;
  if (!reqState.start) reqState.start = nowMs;
  props.setProperty(otpReqKey, JSON.stringify(reqState));

  var otpNum = Math.floor(Math.random() * 900000) + 100000;
  var otp = String(otpNum);
  while (otp.length < 6) otp = '0' + otp;

  var otpKey = 'otp_' + emailHash;
  props.setProperty(otpKey, JSON.stringify({ code: otp, expiresAt: nowMs + (OTP_TTL_SECONDS * 1000), attempts: 0 }));

  try {
    MailApp.sendEmail({
      to: p.email,
      subject: 'Your DigiVeritaz verification code',
      name: 'DigiVeritaz',
      replyTo: 'info@digiveritaz.com',
      body: 'Hi ' + (p.fullname || 'there') + ',\n\n' +
            'Your DigiVeritaz verification code is: ' + otp + '\n\n' +
            'It expires in 10 minutes. If you did not request this, you can ignore this email.\n\n— DigiVeritaz',
      htmlBody: buildOtpEmail_(p.fullname, otp)
    });
  } catch (mailErr) {
    console.error('OTP mail failed: ' + mailErr);
    return json({ ok: false, error: 'mail_failed', detail: String(mailErr) });
  }

  return json({ ok: true, message: 'code_sent' });
}

// ============================================================
// ACTION 2 — submit_form  (legacy email-OTP fallback)
// ============================================================
function handleSubmitForm_(p, nowMs) {
  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var f = REQUIRED_FIELDS[i];
    if (!p[f] || String(p[f]).trim() === '') { return json({ ok: false, error: 'missing_field:' + f }); }
  }
  var phoneDigits = (p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8 || phoneDigits.length > 15) { return json({ ok: false, error: 'bad_phone' }); }
  if (!p.otp || !/^\d{6}$/.test(p.otp)) { return json({ ok: false, error: 'otp_required' }); }

  var props = PropertiesService.getScriptProperties();
  var emailHash = hash_(String(p.email).toLowerCase());

  var otpKey = 'otp_' + emailHash;
  var rawOtp = props.getProperty(otpKey);
  if (!rawOtp) return json({ ok: false, error: 'otp_not_requested' });
  var stored = safeParse_(rawOtp, null);
  if (!stored) { props.deleteProperty(otpKey); return json({ ok: false, error: 'otp_not_requested' }); }
  if (nowMs > stored.expiresAt) { props.deleteProperty(otpKey); return json({ ok: false, error: 'otp_expired' }); }
  if ((stored.attempts || 0) >= OTP_MAX_ATTEMPTS) { props.deleteProperty(otpKey); return json({ ok: false, error: 'otp_attempts_exceeded' }); }
  if (stored.code !== String(p.otp)) {
    stored.attempts = (stored.attempts || 0) + 1;
    props.setProperty(otpKey, JSON.stringify(stored));
    return json({ ok: false, error: 'otp_wrong' });
  }
  props.deleteProperty(otpKey);

  var dedupKey = 'dedup_' + hash_(String(p.email).toLowerCase() + '|' + phoneDigits);
  var lastSeen = parseInt(props.getProperty(dedupKey) || '0', 10);
  if (!isNaN(lastSeen) && (nowMs - lastSeen) < (DEDUP_WINDOW_SECONDS * 1000)) {
    return json({ ok: false, error: 'duplicate_submission' });
  }
  props.setProperty(dedupKey, String(nowMs));

  var rateKey = 'rate_' + emailHash;
  var rateState = safeParse_(props.getProperty(rateKey), { count: 0, start: 0 });
  if (nowMs - rateState.start > 3600000) { rateState = { count: 0, start: nowMs }; }
  if (rateState.count >= HOURLY_CAP_PER_EMAIL) { return json({ ok: false, error: 'rate_limited' }); }
  rateState.count += 1;
  if (!rateState.start) rateState.start = nowMs;
  props.setProperty(rateKey, JSON.stringify(rateState));

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) return json({ ok: false, error: 'Sheet "' + SHEET_NAME + '" not found' });

  var services = pickServices_(p);
  sheet.appendRow([
    new Date(), safeCell_(p.fullname || p.name || ''), safeCell_(p.email || ''),
    safeCell_(p.phone || ''), safeCell_(p.company || ''), safeCell_(p.budget || ''),
    safeCell_(services), safeCell_(p.message || ''), safeCell_(p._page || ''),
    safeCell_(p._source || 'contact-us form'), 'Complete', safeCell_(p.otp_verified || 'email'), ''
  ]);
  writeAttr_(sheet, sheet.getLastRow(), p);   // campaign cells, by header name

  postLeadToCRM_(p, services);  // CRM — also send this completed lead to the CRM

  try { sendNotification_(p, services); } catch (notifyErr) { console.error('Notify mail failed: ' + notifyErr); }
  try { sendUserAck_(p); } catch (ackErr) { console.error('User ack failed: ' + ackErr); }  // USER-ACK

  return json({ ok: true });
}

// ============================================================
// ACTION 3 — lead_save  (phone-OTP forms: both popups + contact page)
// Upserts by Lead ID so a lead is ONE row: Partial when the number is entered,
// updated to Complete on submit. Emails the team only on the Complete lead.
// ============================================================
function handleLeadSave_(p, nowMs) {
  var phoneDigits = (p.phone || '').replace(/\D+/g, '');
  if (phoneDigits.length < 8 || phoneDigits.length > 15) return json({ ok: false, error: 'bad_phone' });

  var complete = (p.complete === '1' || p.status === 'Complete');
  if (complete) {
    if (!(p.fullname || p.name)) return json({ ok: false, error: 'missing_field:fullname' });
    if (!p.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(p.email)) return json({ ok: false, error: 'bad_email' });
  }

  var leadId   = (p.leadId || '').toString().trim();
  var services = pickServices_(p);
  var row = [
    new Date(), safeCell_(p.fullname || p.name || ''), safeCell_(p.email || ''),
    safeCell_(p.phone || ''), safeCell_(p.company || ''), safeCell_(p.budget || ''),
    safeCell_(services), safeCell_(p.message || ''), safeCell_(p._page || ''),
    safeCell_(p._source || 'website'), safeCell_(complete ? 'Complete' : 'Partial'),
    safeCell_(p.otp_verified || ''), safeCell_(leadId)
  ];

  var lock = LockService.getScriptLock();
  try { lock.waitLock(10000); } catch (e) {}
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    if (!sheet) return json({ ok: false, error: 'Sheet "' + SHEET_NAME + '" not found' });
    var rowIndex = leadId ? findRowByLeadId_(sheet, leadId) : -1;
    if (rowIndex > 0) { sheet.getRange(rowIndex, 1, 1, row.length).setValues([row]); }  // update this lead's row
    else { sheet.appendRow(row); rowIndex = sheet.getLastRow(); }                        // first time we see this lead
    writeAttr_(sheet, rowIndex, p);                                                     // campaign cells, by header name
  } finally { try { lock.releaseLock(); } catch (e) {} }

  // Email the team only ONCE, on the Complete submission.
  if (complete) {
    postLeadToCRM_(p, services);  // CRM — send the completed lead to the CRM
    var props = PropertiesService.getScriptProperties();
    var dedupKey = 'dedup_' + hash_(String(p.email).toLowerCase() + '|' + phoneDigits);
    var lastSeen = parseInt(props.getProperty(dedupKey) || '0', 10);
    if (isNaN(lastSeen) || (nowMs - lastSeen) >= (DEDUP_WINDOW_SECONDS * 1000)) {
      props.setProperty(dedupKey, String(nowMs));
      try { sendNotification_(p, services); } catch (e) { console.error('Notify failed: ' + e); }
      try { sendUserAck_(p); } catch (e) { console.error('User ack failed: ' + e); }  // USER-ACK
    }
  }
  return json({ ok: true });
}

// ============================================================
// Campaign attribution — written BY HEADER NAME, not by fixed position.
// Put any of these headers in row 1, in ANY column (P, Z, wherever) and it fills:
//     utm_source | utm_medium | utm_campaign | utm_content | click_id
// Or use ONE combined column headed:  campaign     -> "google / cpc / brand-search"
// Headers you leave out are skipped; nothing else on the row moves.
// ============================================================
function writeAttr_(sheet, rowIndex, p) {
  try {
    if (!sheet || !rowIndex || rowIndex < 2) return;
    var lastCol = sheet.getLastColumn();
    if (lastCol < 1) return;
    var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
    var norm = [];
    for (var i = 0; i < headers.length; i++) {
      norm.push(String(headers[i] == null ? '' : headers[i]).trim().toLowerCase().replace(/\s+/g, '_'));
    }
    var src = p.utm_source || '', med = p.utm_medium || '', camp = p.utm_campaign || '';
    var vals = {
      utm_source:   src,
      utm_medium:   med,
      utm_campaign: camp,
      utm_content:  p.utm_content || p.utm_term || '',
      click_id:     p.gclid || p.gbraid || p.wbraid || '',
      campaign:     [src, med, camp].filter(String).join(' / ')
    };
    for (var key in vals) {
      if (!Object.prototype.hasOwnProperty.call(vals, key)) continue;
      var col = norm.indexOf(key);
      if (col >= 0 && vals[key]) sheet.getRange(rowIndex, col + 1).setValue(safeCell_(vals[key]));
    }
  } catch (err) {
    console.error('writeAttr_ failed: ' + err);   // never block the lead save
  }
}

function findRowByLeadId_(sheet, leadId) {
  var last = sheet.getLastRow();
  if (last < 2) return -1;
  var ids = sheet.getRange(2, 13, last - 1, 1).getValues(); // column M = Lead ID
  for (var r = 0; r < ids.length; r++) {
    if (String(ids[r][0]) === leadId) return r + 2;
  }
  return -1;
}

// ============================================================
// CRM — push a completed lead to the CRM webhook (best-effort).
// ============================================================
function postLeadToCRM_(p, services) {
  try {
    var payload = {
      fullname:     p.fullname || p.name || '',
      email:        p.email || '',
      phone:        p.phone || '',
      company:      p.company || '',
      budget:       p.budget || '',
      'services[]': services ? String(services).split(',').map(function (s) { return s.trim(); }).filter(String) : [],
      message:      p.message || '',
      otp_verified: p.otp_verified || '',
      status:       'Complete',
      leadId:       p.leadId || '',
      _source:      p._source || 'website',
      _page:        p._page || '',
      utm_source:   p.utm_source || '',
      utm_medium:   p.utm_medium || '',
      utm_campaign: p.utm_campaign || '',
      utm_term:     p.utm_term || '',
      utm_content:  p.utm_content || '',
      gclid:        p.gclid || p.gbraid || p.wbraid || '',
      gad_campaignid: p.gad_campaignid || '',
      device:       p.device || '',
      landing_page: p.landing_page || '',
      referrer:     p.referrer || ''
    };
    UrlFetchApp.fetch(CRM_WEBHOOK_URL, {
      method: 'post',
      contentType: 'application/json',
      headers: { 'X-Webhook-Secret': CRM_WEBHOOK_SECRET },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
  } catch (err) {
    console.error('CRM push failed: ' + err);  // Sheet + email already succeeded
  }
}

// ============================================================
// CRM — return every DV Lead Form row (Partial + Complete) as JSON,
// values exactly as displayed in the sheet (13 columns A–M).
// ============================================================
function readAllLeadRows_() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) return [];
  var values = sheet.getDataRange().getDisplayValues();
  if (values.length < 2) return [];
  var base = ['timestamp','name','email','phone','company','budget','services','message','page','source','status','otp_verified','leadId'];
  var keys = base.slice();
  for (var h = base.length; h < values[0].length; h++) {            // extra columns keyed by their own header
    keys.push(String(values[0][h] || ('col' + (h + 1))).trim().toLowerCase().replace(/\s+/g, '_'));
  }
  var out = [];
  for (var r = 1; r < values.length; r++) {
    var row = values[r], obj = {};
    for (var c = 0; c < keys.length; c++) obj[keys[c]] = (row[c] == null ? '' : String(row[c]));
    out.push(obj);
  }
  return out;
}

// ============================================================
// HELPERS
// ============================================================
function parseRequest(e) {
  if (!e) return null;
  if (e.postData && e.postData.type === 'application/json') {
    try { return JSON.parse(e.postData.contents); } catch (jerr) { return null; }
  }
  var out = {};
  if (e.parameter) { for (var k in e.parameter) { if (Object.prototype.hasOwnProperty.call(e.parameter, k)) out[k] = e.parameter[k]; } }
  if (e.parameters) { out.__multi__ = e.parameters; }
  return out;
}

function pickServices_(p) {
  var multi = p.__multi__ || {};
  if (Array.isArray(multi['services[]']) && multi['services[]'].length > 1) { return multi['services[]'].join(', '); }
  if (Array.isArray(multi.services) && multi.services.length > 1) { return multi.services.join(', '); }
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
    '-----------------------------------------\n' +
    'Name:     ' + name + '\n' +
    'Email:    ' + email + '\n' +
    'Phone:    ' + (p.phone   || '') + '\n' +
    'Company:  ' + company + '\n' +
    'Budget:   ' + (p.budget  || '') + '\n' +
    'Services: ' + services + '\n' +
    '-----------------------------------------\n\n' +
    'Message:\n' + (p.message || '(none)') + '\n\n' +
    '-----------------------------------------\n' +
    'Page:     ' + (p._page   || '') + '\n' +
    'Source:   ' + (p._source || 'website') + '\n' +
    'Campaign: ' + [(p.utm_source||''), (p.utm_medium||''), (p.utm_campaign||'')].filter(String).join(' / ') +
                   (p.gclid ? '  (gclid ' + p.gclid + ')' : '') + '\n' +
    'Time:     ' + new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST\n';
  MailApp.sendEmail({ to: NOTIFY_EMAILS, subject: subject, name: 'DigiVeritaz Website', replyTo: email || undefined, body: body });
}

// ============================================================
// USER-ACK — thank-you email to the person who submitted (Complete only).
// Best-effort: never blocks the lead save; skips if no valid email.
// ============================================================
function sendUserAck_(p) {
  var to = (p.email || '').toString().trim();
  if (!to || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(to)) return;   // no valid email -> skip
  var name = (p.fullname || p.name || '').toString().trim();
  var hi = name ? name.split(' ')[0] : 'there';               // first name if we have it
  MailApp.sendEmail({
    to: to,
    subject: 'Thank you for contacting DigiVeritaz',
    name: 'DigiVeritaz',
    replyTo: 'info@digiveritaz.com',
    body: 'Hi ' + hi + ',\n\n' +
          'Thank you for filling out the form on DigiVeritaz. We have received your ' +
          'details and our team will reach out to you shortly — usually within one ' +
          'business day.\n\n' +
          'If it is urgent, call us at +91 99566 55662.\n\n' +
          '— Team DigiVeritaz\nhttps://www.digiveritaz.com',
    htmlBody: buildAckEmail_(hi)
  });
}

function buildAckEmail_(hi) {
  return '' +
    '<div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;border:1px solid #e5e7eb;border-radius:12px">' +
      '<h2 style="color:#16a34a;margin:0 0 12px">Thank you for reaching out!</h2>' +
      '<p style="color:#111827">Hi ' + htmlEscape_(hi) + ',</p>' +
      '<p style="color:#374151;line-height:1.6">Thanks for filling out the form on <strong>DigiVeritaz</strong>. ' +
        'We have received your details and our team will get back to you shortly — usually ' +
        '<strong>within one business day</strong>.</p>' +
      '<p style="text-align:center;margin:22px 0">' +
        '<a href="https://www.digiveritaz.com" style="background:#16a34a;color:#fff;text-decoration:none;padding:12px 26px;border-radius:999px;font-weight:600;display:inline-block">Visit DigiVeritaz</a>' +
      '</p>' +
      '<p style="color:#6b7280;font-size:.9rem;line-height:1.6">Need us sooner? Call ' +
        '<a href="tel:+919956655662" style="color:#16a34a">+91 99566 55662</a> or just reply to this email.</p>' +
      '<p style="color:#6b7280;font-size:.85rem;margin-top:18px">— Team DigiVeritaz</p>' +
    '</div>';
}

// Run in editor (Run > diagMail) to confirm sending. Set DIAG_TO first.
var DIAG_TO = ''; // <-- put your test email here, e.g. 'you@gmail.com'
function diagMail() {
  var quota = MailApp.getRemainingDailyQuota();
  Logger.log('Remaining daily email quota: ' + quota);
  if (!DIAG_TO) { Logger.log('Set DIAG_TO (top of file) to your email, then run again.'); return; }
  MailApp.sendEmail({ to: DIAG_TO, subject: 'DigiVeritaz mail diagnostic', name: 'DigiVeritaz',
    body: 'If you received this, the script CAN send email.\nQuota remaining: ' + quota });
  Logger.log('Diagnostic email sent to ' + DIAG_TO + '. Check inbox AND Spam.');
}

function buildOtpEmail_(fullname, code) {
  var who = (fullname && String(fullname).trim()) ? htmlEscape_(String(fullname).trim()) : 'there';
  return '' +
    '<div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:20px;border:1px solid #e5e7eb;border-radius:12px">' +
      '<h2 style="color:#16a34a;margin:0 0 12px">DigiVeritaz — Verification Code</h2>' +
      '<p>Hi ' + who + ',</p>' +
      '<p>Use this 6-digit code to complete your submission. It expires in 10 minutes.</p>' +
      '<div style="font-size:2rem;letter-spacing:0.5em;font-weight:bold;text-align:center;padding:20px;background:#f3f4f6;border-radius:12px;color:#111827">' +
        htmlEscape_(code) +
      '</div>' +
      '<p style="margin-top:20px;color:#6b7280;font-size:.9rem">If you did not request this code, you can ignore this email.</p>' +
    '</div>';
}

function stripInvisible_(s) {
  if (s == null) return s;
  var out = '', src = String(s);
  for (var i = 0; i < src.length; i++) {
    var c = src.charCodeAt(i);
    if (c >= 0x200B && c <= 0x200F) continue;
    if (c >= 0x2028 && c <= 0x202F) continue;
    if (c >= 0x2060 && c <= 0x206F) continue;
    if (c === 0xFEFF) continue;
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
  if (first === '=' || first === '+' || first === '-' || first === '@' || first === '\t' || first === '\r') { return "'" + str; }
  return str;
}

function hash_(s) {
  var raw = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, String(s));
  var b64 = Utilities.base64Encode(raw);
  return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '').substring(0, 16);
}

function htmlEscape_(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function safeParse_(raw, fallback) {
  if (!raw) return fallback;
  try { return JSON.parse(raw); } catch (e) { return fallback; }
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
