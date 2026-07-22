/* POST /api/otp-send  { name, email }  ->  { ok:true, token }
 *
 * Generates a 6-digit code, emails it via Resend, and returns a signed stateless
 * token carrying the keyed digest of that code. The plaintext code exists only in
 * the email and in this function's memory — it is never sent back to the browser.
 */
const crypto = require('node:crypto');
const H = require('./_otp.js');

module.exports = async (req, res) => {
  H.cors(req, res);
  if (req.method === 'OPTIONS') return res.status(204).end();
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
    return res.status(502).json({ ok: false, error: 'mail_failed' });
  }

  const token = H.issueToken({
    e: email,
    n: name,
    c: H.codeDigest(email, code),
    x: Date.now() + H.OTP_TTL_MS
  });

  return res.status(200).json({ ok: true, token });
};

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
