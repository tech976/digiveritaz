/* Shared helpers for the AI News OTP endpoints.
 *
 * OTP state is carried in a signed, stateless token rather than a database.
 * /api/otp-send returns the token, the browser hands it back to /api/otp-verify,
 * and the server re-derives the expected value. No KV, no Redis, no cleanup job.
 *
 * The code itself is stored as HMAC(secret, email|code) — NOT a bare hash. A bare
 * SHA-256 of a 6-digit code is brute-forceable offline in milliseconds, which would
 * let an attacker request a code for someone else's address, crack it from the token
 * they were handed, and subscribe that person without consent. Keying the digest with
 * a server-only secret removes that path: candidates cannot be computed without it.
 */
const crypto = require('node:crypto');

const OTP_TTL_MS = 10 * 60 * 1000;

function b64url(buf) {
  return Buffer.from(buf).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function unb64url(s) {
  return Buffer.from(String(s).replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8');
}

function secret() {
  const s = process.env.OTP_SECRET;
  if (!s) throw new Error('OTP_SECRET is not set');
  return s;
}

function hmac(data) {
  return crypto.createHmac('sha256', secret()).update(data).digest('hex');
}

function codeDigest(email, code) {
  return hmac('code|' + String(email).trim().toLowerCase() + '|' + String(code));
}

/** token = base64url(JSON payload) + "." + hmac(payload) */
function issueToken(payload) {
  const body = b64url(JSON.stringify(payload));
  return body + '.' + hmac('tok|' + body);
}

function readToken(token) {
  if (typeof token !== 'string' || token.indexOf('.') < 0) return null;
  const [body, sig] = token.split('.');
  const expect = hmac('tok|' + body);
  // constant-time compare so signature checking cannot be timed
  const a = Buffer.from(String(sig));
  const b = Buffer.from(expect);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try { return JSON.parse(unb64url(body)); } catch { return null; }
}

function validEmail(v) {
  return typeof v === 'string' && /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(v.trim()) && v.length <= 254;
}

/** Strip control characters (incl. CR/LF, which could allow header injection). */
function clean(v, max) {
  return String(v == null ? '' : v).replace(/[\x00-\x1F\x7F]/g, '').trim().slice(0, max || 120);
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/** Send through Resend. Returns {ok} or {ok:false, status, detail}. */
async function sendMail({ to, subject, html, text }) {
  const key = process.env.RESEND_API_KEY;
  if (!key) return { ok: false, status: 0, detail: 'RESEND_API_KEY is not set' };
  // Must be an address on a domain verified in Resend, or every send is rejected.
  const from = process.env.NEWS_FROM || 'DigiVeritaz AI News <tech@digiveritaz.com>';

  let r;
  try {
    r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to: [to], subject, html, text, reply_to: 'info@digiveritaz.com' })
    });
  } catch (e) {
    return { ok: false, status: 0, detail: String(e) };
  }
  if (!r.ok) return { ok: false, status: r.status, detail: await r.text().catch(() => '') };
  return { ok: true };
}

/** Same-origin in production; the allow-list only matters for previews. */
function cors(req, res) {
  const origin = req.headers.origin || '';
  const ok = /^https?:\/\/(www\.digiveritaz\.com|localhost(:\d+)?|127\.0\.0\.1(:\d+)?)$/.test(origin) ||
             /^https:\/\/[a-z0-9-]+\.vercel\.app$/.test(origin);
  if (ok) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function body(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch { return {}; } }
  return {};
}

module.exports = {
  OTP_TTL_MS, codeDigest, issueToken, readToken, validEmail, clean, esc, sendMail, cors, body
};
