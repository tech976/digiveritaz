/**
 * DigiVeritaz Contact Form — Hardened Apps Script Endpoint
 * Deploy as a Web App (Execute as: Me, Access: Anyone).
 * Required Script Property: TURNSTILE_SECRET (Cloudflare Turnstile secret key).
 */

// ---------- CONSTANTS ----------
var SHEET_NAME = 'DV Lead Form';
var REQUIRED_FIELDS = ['fullname', 'email', 'phone'];
var HONEYPOT_FIELDS = ['_honey', 'website', 'address_line'];
var MAX_FIELD_LEN = 2000;
var MIN_TIME_ON_PAGE_MS = 3000;          // <3s on page = bot
var MAX_TIME_ON_PAGE_MS = 7200000;       // >2h on page = stale/replayed
var DEDUP_WINDOW_SECONDS = 60;
var HOURLY_CAP_PER_EMAIL = 5;
var NOTIFICATION_EMAIL = 'campaign@digiveritaz.com';
var TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';

// ---------- ENTRY POINT ----------
function doPost(e) {
  try {
    // Step 1: payload presence
    var p = e && e.parameter;
    if (!p) {
      return reply_({ ok: false, error: 'no_payload' });
    }

    // Step 2: honeypot — silently accept (return ok) without writing a row
    for (var h = 0; h < HONEYPOT_FIELDS.length; h++) {
      var hv = p[HONEYPOT_FIELDS[h]];
      if (hv && String(hv).trim() !== '') {
        return reply_({ ok: true });
      }
    }

    // Step 3: strip invisible characters from every string param
    for (var k in p) {
      if (Object.prototype.hasOwnProperty.call(p, k) && typeof p[k] === 'string') {
        p[k] = stripInvisible_(p[k]);
      }
    }

    // Step 4: required fields
    for (var r = 0; r < REQUIRED_FIELDS.length; r++) {
      var f = REQUIRED_FIELDS[r];
      if (!p[f] || String(p[f]).trim() === '') {
        return reply_({ ok: false, error: 'missing_field:' + f });
      }
    }

    // Step 5: _jsok pattern check
    var jsok = p._jsok || '';
    if (!/^dv-[a-z0-9]{8,12}$/.test(jsok)) {
      return reply_({ ok: false, error: 'no_js' });
    }

    // Step 6: time-on-page check
    var ts = parseInt(p._ts, 10);
    var now = Date.now();
    if (isNaN(ts) || ts > now || (now - ts) > MAX_TIME_ON_PAGE_MS || (now - ts) < MIN_TIME_ON_PAGE_MS) {
      return reply_({ ok: false, error: 'invalid_timing' });
    }

    // Step 7: format checks
    var email = String(p.email).trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return reply_({ ok: false, error: 'bad_email' });
    }
    var phoneDigits = String(p.phone).replace(/\D+/g, '');
    if (phoneDigits.length < 8 || phoneDigits.length > 15) {
      return reply_({ ok: false, error: 'bad_phone' });
    }

    // Step 8: length cap — truncate to MAX_FIELD_LEN
    for (var k2 in p) {
      if (Object.prototype.hasOwnProperty.call(p, k2) && typeof p[k2] === 'string' && p[k2].length > MAX_FIELD_LEN) {
        p[k2] = p[k2].substring(0, MAX_FIELD_LEN);
      }
    }

    // Step 9: Turnstile verification
    var secret = PropertiesService.getScriptProperties().getProperty('TURNSTILE_SECRET');
    if (!secret) {
      console.warn('TURNSTILE_SECRET not configured — skipping challenge verification');
    } else {
      var tsResp = UrlFetchApp.fetch(TURNSTILE_VERIFY_URL, {
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        payload: 'secret=' + encodeURIComponent(secret) + '&response=' + encodeURIComponent(p['cf-turnstile-response'] || ''),
        muteHttpExceptions: true
      });
      var tsBody = {};
      try {
        tsBody = JSON.parse(tsResp.getContentText() || '{}');
      } catch (jerr) {
        tsBody = {};
      }
      if (tsBody.success !== true) {
        return reply_({ ok: false, error: 'failed_challenge' });
      }
    }

    // Step 10: dedup + rate limit
    var props = PropertiesService.getScriptProperties();
    var phone = String(p.phone).trim();
    var dedupKey = 'last_' + hash_(email + '|' + phone);
    var lastSubmit = parseInt(props.getProperty(dedupKey) || '0', 10);
    if (now - lastSubmit < DEDUP_WINDOW_SECONDS * 1000) {
      return reply_({ ok: false, error: 'duplicate' });
    }

    var rateKey = 'count_' + hash_(email);
    var rate;
    try {
      rate = JSON.parse(props.getProperty(rateKey) || '{"count":0,"start":0}');
    } catch (perr) {
      rate = { count: 0, start: 0 };
    }
    if (now - rate.start > 3600000) {
      rate = { count: 0, start: now };
    }
    if (rate.count >= HOURLY_CAP_PER_EMAIL) {
      return reply_({ ok: false, error: 'rate_limited' });
    }
    rate.count = rate.count + 1;
    props.setProperty(rateKey, JSON.stringify(rate));
    props.setProperty(dedupKey, String(now));

    // Step 12: append to sheet
    var fullname = String(p.fullname).trim();
    var company = p.company ? String(p.company).trim() : '';
    var budget = p.budget ? String(p.budget).trim() : '';
    var message = p.message ? String(p.message).trim() : '';
    var subject = p._subject ? String(p._subject).trim() : 'contact-us form';

    // services may be repeated form field: services, services[], or comma list
    var services = '';
    if (Array.isArray(p.services)) {
      services = p.services.join(', ');
    } else if (typeof p.services === 'string') {
      services = p.services;
    } else if (Array.isArray(p['services[]'])) {
      services = p['services[]'].join(', ');
    } else if (typeof p['services[]'] === 'string') {
      services = p['services[]'];
    }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow(['Timestamp', 'Name', 'Email', 'Phone', 'Company', 'Budget', 'Services', 'Message', 'Subject']);
    }
    sheet.appendRow([
      new Date(),
      safeCell_(fullname),
      safeCell_(email),
      safeCell_(phone),
      safeCell_(company),
      safeCell_(budget),
      safeCell_(services),
      safeCell_(message),
      safeCell_(subject || 'contact-us form')
    ]);

    // Step 13: notification email
    try {
      MailApp.sendEmail({
        to: NOTIFICATION_EMAIL,
        subject: 'New lead: ' + fullname + ' (' + budget + ')',
        htmlBody: buildEmail_({
          fullname: fullname,
          email: email,
          phone: phone,
          company: company,
          budget: budget,
          message: message
        }, services)
      });
    } catch (merr) {
      console.error('MailApp.sendEmail failed: ' + (merr && merr.message ? merr.message : merr));
    }

    // Step 14: success
    return reply_({ ok: true });
  } catch (err) {
    console.error('doPost exception: ' + (err && err.stack ? err.stack : err));
    return reply_({ ok: false, error: 'server_error' });
  }
}

// ---------- HELPERS ----------

function reply_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function stripInvisible_(s) {
  if (typeof s !== 'string') return s;
  // Remove U+200B..U+200F, U+FEFF (BOM), U+2028, U+2029, and carriage returns
  return s
    .replace(new RegExp('[\\u200B-\\u200F]', 'g'), '')
    .replace(new RegExp('\\uFEFF', 'g'), '')
    .replace(new RegExp('[\\u2028\\u2029]', 'g'), '')
    .replace(/\r/g, '');
}

function safeCell_(s) {
  if (s === null || s === undefined) return '';
  var str = String(s);
  if (str.length === 0) return '';
  if (/^[=+\-@\t\r]/.test(str)) {
    return "'" + str;
  }
  return str;
}

function hash_(s) {
  var bytes = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, String(s));
  var b64 = Utilities.base64EncodeWebSafe(bytes);
  return b64.substring(0, 16);
}

function htmlEscape_(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function buildEmail_(p, services) {
  var rows = [
    ['Name', p.fullname],
    ['Email', p.email],
    ['Phone', p.phone],
    ['Company', p.company],
    ['Budget', p.budget],
    ['Services', services],
    ['Message', p.message]
  ];
  var html = '<table style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px">';
  for (var i = 0; i < rows.length; i++) {
    var label = htmlEscape_(rows[i][0]);
    var value = htmlEscape_(rows[i][1] || '');
    html += '<tr>' +
      '<td style="padding:6px 12px;border:1px solid #ddd;background:#f7f7f7;font-weight:bold;vertical-align:top">' + label + '</td>' +
      '<td style="padding:6px 12px;border:1px solid #ddd;vertical-align:top">' + value + '</td>' +
      '</tr>';
  }
  html += '</table>';
  return html;
}
