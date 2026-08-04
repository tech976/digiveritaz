/**
 * === DigiVeritaz Careers / Recruitment Form — v1 ===
 * REPO REFERENCE COPY — this is a version-control snapshot only. The LIVE script runs
 * as a Google Apps Script Web App in the DigiVeritaz Google account and must be updated
 * by pasting this into the Apps Script editor and redeploying (Manage deployments ->
 * New version, same /exec URL). Pushing this file to git does NOT deploy it.
 *
 * SEPARATE from the lead form. This must be bound to its OWN spreadsheet so job
 * applicants never land in the sales pipeline. Do not reuse the lead-form /exec URL.
 *
 * ---------------------------------------------------------------------------
 * SETUP (once)
 *   1. Create a new Google Sheet, e.g. "DV Careers Applications".
 *   2. Extensions -> Apps Script. Delete the stub, paste this file, Save.
 *   3. Set NOTIFY_EMAILS below to whoever should get applications.
 *   4. Deploy -> New deployment -> type "Web app"
 *        Execute as:        Me
 *        Who has access:    Anyone
 *      Copy the /exec URL it gives you.
 *   5. Put that URL in CAREERS_ENDPOINT in build_careers_page.py and re-run it.
 * ---------------------------------------------------------------------------
 */

// ============================================================
// CONFIG
// ============================================================
var SHEET_NAME = 'Applications';
var NOTIFY_EMAILS = [
  'gulaboshaikh@digiveritaz.com',
  'durvamukherjee@digiveritaz.com',
  'hr@digiveritaz.com'
].join(',');
var SUBJECT_PREFIX = 'New Application';
var SEND_APPLICANT_ACK = true;

// ============================================================
// HARDENING
// ============================================================
var REQUIRED_FIELDS = ['fullname', 'email', 'phone', 'role'];
var HONEYPOT_FIELDS = ['_hp_site', '_hp_addr', '_honey'];
var MAX_FIELD_LEN = 2000;
var MIN_TIME_ON_PAGE_MS = 3000;
var MAX_TIME_ON_PAGE_MS = 172800000;   // 48h, so a long-open tab is not dropped
var DEDUP_WINDOW_SECONDS = 60;

// Column order in the sheet. Add to the END only — inserting in the middle
// shifts every existing row's data.
var COLUMNS = [
  'Timestamp', 'Application ID', 'Role', 'Full Name', 'Email', 'Phone',
  'City', 'Experience', 'Qualification', 'Availability',
  'Resume Link', 'Portfolio Link', 'LinkedIn', 'Expected Pay',
  'AI Tools', 'Heard Via', 'Note', 'Consent', 'OTP Verified', 'Page', 'Source',
  'UTM Source', 'UTM Medium', 'UTM Campaign', 'Referrer'
];

// ============================================================
function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};

    for (var i = 0; i < HONEYPOT_FIELDS.length; i++) {
      if (String(p[HONEYPOT_FIELDS[i]] || '').trim() !== '') return ok('bot');
    }
    if (!p._jsok) return ok('nojs');

    var ts = Number(p._ts || 0);
    if (ts) {
      var elapsed = Date.now() - ts;
      if (elapsed < MIN_TIME_ON_PAGE_MS || elapsed > MAX_TIME_ON_PAGE_MS) return ok('timing');
    }

    for (var j = 0; j < REQUIRED_FIELDS.length; j++) {
      if (!String(p[REQUIRED_FIELDS[j]] || '').trim()) return ok('missing:' + REQUIRED_FIELDS[j]);
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(p.email).trim())) return ok('bademail');

    var appId = String(p.applicationId || '').trim() || ('ca-' + Date.now());
    if (isDuplicate(appId)) return ok('dupe');

    var sheet = getSheet();
    sheet.appendRow([
      new Date(),
      appId,
      clip(p.role), clip(p.fullname), clip(p.email), clip(p.phone),
      clip(p.city), clip(p.experience), clip(p.education), clip(p.availability),
      clip(p.resume_link), clip(p.portfolio_link), clip(p.linkedin), clip(p.expected_pay),
      clip(p.ai_tools), clip(p.source), clip(p.note), clip(p.consent), clip(p.otp_verified),
      clip(p._page), clip(p._source),
      clip(p.utm_source), clip(p.utm_medium), clip(p.utm_campaign), clip(p.referrer)
    ]);

    notify(p, appId);
    if (SEND_APPLICANT_ACK) ackApplicant(p);
    return ok('saved');

  } catch (err) {
    // 200 with ok:false — Cloudflare in front of the site eats non-200s.
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Visit <exec-url>?debug=1 to see which spreadsheet this script is actually
// bound to, what tabs exist, and whether mail quota is available.
function doGet(e) {
  if (e && e.parameter && e.parameter.debug === '1') {
    var out = {};
    try {
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      out.boundSpreadsheet = ss ? ss.getName() : null;
      out.spreadsheetUrl   = ss ? ss.getUrl() : null;
      out.tabs = ss ? ss.getSheets().map(function (s) {
        return s.getName() + ' (rows: ' + s.getLastRow() + ')';
      }) : [];
      out.runningAs = Session.getEffectiveUser().getEmail();
      out.mailQuotaLeft = MailApp.getRemainingDailyQuota();
      out.notifyList = NOTIFY_EMAILS;
      out.subjectPrefix = SUBJECT_PREFIX;
    } catch (err) {
      out.error = String(err);
    }
    return ContentService.createTextOutput(JSON.stringify(out, null, 2))
      .setMimeType(ContentService.MimeType.JSON);
  }
  return ok('alive');
}

// ============================================================
// helpers
// ============================================================
function ok(status) {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true, status: status }))
    .setMimeType(ContentService.MimeType.JSON);
}

function clip(v) {
  return String(v == null ? '' : v).slice(0, MAX_FIELD_LEN);
}

function getSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(COLUMNS);
    sh.getRange(1, 1, 1, COLUMNS.length).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function isDuplicate(appId) {
  var cache = CacheService.getScriptCache();
  if (cache.get(appId)) return true;
  cache.put(appId, '1', DEDUP_WINDOW_SECONDS);
  return false;
}

function notify(p, appId) {
  if (!NOTIFY_EMAILS) return;
  var lines = [
    'Role:          ' + (p.role || ''),
    'Name:          ' + (p.fullname || ''),
    'Email:         ' + (p.email || ''),
    'Phone:         ' + (p.phone || ''),
    'City:          ' + (p.city || ''),
    'Experience:    ' + (p.experience || ''),
    'Qualification: ' + (p.education || ''),
    'Availability:  ' + (p.availability || ''),
    'Expected pay:  ' + (p.expected_pay || ''),
    '',
    'Resume:        ' + (p.resume_link || ''),
    'Portfolio:     ' + (p.portfolio_link || ''),
    'LinkedIn:      ' + (p.linkedin || ''),
    '',
    'AI tools:      ' + (p.ai_tools || ''),
    'Heard via:     ' + (p.source || ''),
    '',
    'Note:',
    (p.note || '(none)'),
    '',
    '--',
    'Application ID: ' + appId
  ].join('\n');

  MailApp.sendEmail({
    to: NOTIFY_EMAILS,
    subject: SUBJECT_PREFIX + ' — ' + (p.role || 'Open application') + ' — ' + (p.fullname || 'Unknown'),
    body: lines,
    replyTo: String(p.email || '').trim() || undefined
  });
}

function ackApplicant(p) {
  var to = String(p.email || '').trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) return;
  MailApp.sendEmail({
    to: to,
    subject: 'We received your application — DigiVeritaz',
    body: [
      'Hi ' + (String(p.fullname || '').split(' ')[0] || 'there') + ',',
      '',
      'Thanks for applying for the ' + (p.role || 'open') + ' role at DigiVeritaz.',
      'Your application is with our team. We read every one and will be in touch',
      'if there is a fit.',
      '',
      '— DigiVeritaz',
      'https://www.digiveritaz.com/careers/'
    ].join('\n')
  });
}
