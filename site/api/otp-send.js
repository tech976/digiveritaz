/* POST /api/otp-send  { name, email }  ->  { ok:true, token }
 *
 * Generates a 6-digit code, emails it via Resend, and returns a signed stateless
 * token carrying the keyed digest of that code. The plaintext code exists only in
 * the email and in this function's memory — it is never sent back to the browser.
 */
const crypto = require('node:crypto');
const H = require('./_otp.js');

  /* Cloudflare sits in front of Vercel and replaces origin 5xx responses with its
     own "error code: 502" page, destroying the JSON body that explains what broke.
     The browser then fails to parse it and shows a generic message, and there is
     nothing to debug from outside. So application-level failures return HTTP 200
     with ok:false — the client checks the ok field, never the status code. 4xx is
     left alone; Cloudflare passes those through intact. */
module.exports = async (req, res) => {
  try {
    return await handler(req, res);
  } catch (e) {
    // Without this the function dies and the edge returns an opaque 502, which
    // tells the user "something went wrong" and tells us nothing at all.
    console.error('otp-send crashed:', e && e.stack ? e.stack : e);
    return res.status(200).json({ ok: false, error: 'server_error', detail: String(e && e.message || e).slice(0, 200) });
  }
};

async function handler(req, res) {
  H.cors(req, res);
  if (req.method === 'OPTIONS') return res.status(204).end();

  // Config probe — reports only whether things are SET, never their values.
  if (req.method === 'GET' && req.query && req.query.diag === '1') {
    return res.status(200).json({
      ok: true,
      node: process.version,
      hasFetch: typeof fetch === 'function',
      hasResendKey: !!process.env.RESEND_API_KEY,
      resendKeyPrefix: (process.env.RESEND_API_KEY || '').slice(0, 3),
      hasOtpSecret: !!process.env.OTP_SECRET,
      // distinguishes "code default" from "env override" -- without this you cannot
      // tell a stale deploy from a NEWS_FROM that is quietly winning
      newsFromEnvSet: !!process.env.NEWS_FROM,
      // step 2 of the subscribe-key handover: must read true BEFORE the digest
      // service starts enforcing, or every signup 401s in the gap
      hasSubscribeKey: !!process.env.SUBSCRIBE_API_KEY,
      from: process.env.NEWS_FROM || 'DigiVeritaz AI News <tech@digiveritaz.tech>'
    });
  }
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method' });

  const b = H.body(req);
  const email = String(b.email || '').trim().toLowerCase();
  const name = H.clean(b.name, 80);

  if (b.hp) return res.status(200).json({ ok: true, token: 'honeypot' });   // bot
  if (!H.validEmail(email)) return res.status(400).json({ ok: false, error: 'bad_email' });

  const code = String(crypto.randomInt(0, 1000000)).padStart(6, '0');

  const mail = await H.sendMail({
    to: email,
    subject: 'Your DigiVeritaz AI News verification code',
    text: 'Hi ' + (name || 'there') + ',\n\n' +
          'Your verification code for DigiVeritaz AI News is: ' + code + '\n\n' +
          'It expires in 10 minutes. If you did not request this, you can ignore this email.\n\n— DigiVeritaz',
    html: otpHtml(name, code)
  });

  if (!mail.ok) {
    console.error('otp-send: Resend failed', mail.status, mail.detail);
    // Resend's own message (bad key, unverified sender, ...) is the only thing that
    // makes this debuggable from outside; it contains no secret.
    return res.status(200).json({ ok: false, error: 'mail_failed', status: mail.status, detail: String(mail.detail).slice(0, 300) });
  }

  const token = H.issueToken({
    e: email,
    n: name,
    c: H.codeDigest(email, code),
    x: Date.now() + H.OTP_TTL_MS
  });

  return res.status(200).json({ ok: true, token });
}

function otpHtml(name, code) {
  const who = name ? H.esc(name) : 'there';
  return '' +
  '<div style="font-family:Arial,Helvetica,sans-serif;max-width:520px;margin:0 auto;padding:24px;border:1px solid #e5e7eb;border-radius:12px">' +
    '<h2 style="color:#16a34a;margin:0 0 14px;font-size:20px">DigiVeritaz AI News — Verification Code</h2>' +
    '<p style="margin:0 0 10px">Hi ' + who + ',</p>' +
    '<p style="margin:0 0 18px">Use this 6-digit code to confirm your subscription. It expires in 10 minutes.</p>' +
    '<div style="font-size:32px;letter-spacing:12px;font-weight:bold;text-align:center;padding:20px;background:#f3f4f6;border-radius:12px;color:#111827">' +
      H.esc(code) +
    '</div>' +
    '<p style="margin-top:20px;color:#6b7280;font-size:13px">If you did not request this, you can safely ignore this email.</p>' +
  '</div>';
}
