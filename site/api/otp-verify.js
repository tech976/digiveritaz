/* POST /api/otp-verify  { token, code }  ->  { ok:true }
 *
 * Verifies the code against the signed token, then registers the subscriber and
 * sends the welcome email. The email address comes out of the SIGNED TOKEN, not
 * the request body — otherwise someone could verify a code for their own address
 * and swap in a victim's address at the last step.
 */
const crypto = require('node:crypto');
const H = require('./_otp.js');

const SUBSCRIBE_URL = process.env.SUBSCRIBE_API_URL ||
  'https://email-automation-blond-nine.vercel.app/api/subscribers';

module.exports = async (req, res) => {
  H.cors(req, res);
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method' });

  const b = H.body(req);
  const code = String(b.code || '').trim();
  if (!/^\d{6}$/.test(code)) return res.status(400).json({ ok: false, error: 'otp_invalid' });

  const t = H.readToken(b.token);
  if (!t) return res.status(400).json({ ok: false, error: 'otp_expired' });
  if (!t.x || Date.now() > t.x) return res.status(400).json({ ok: false, error: 'otp_expired' });

  const email = String(t.e || '').trim().toLowerCase();
  const name = H.clean(t.n, 80);
  if (!H.validEmail(email)) return res.status(400).json({ ok: false, error: 'otp_expired' });

  // constant-time compare of the keyed digest
  const got = Buffer.from(H.codeDigest(email, code));
  const want = Buffer.from(String(t.c || ''));
  if (got.length !== want.length || !crypto.timingSafeEqual(got, want)) {
    return res.status(400).json({ ok: false, error: 'otp_invalid' });
  }

  // ---- register with the digest service -----------------------------------
  let sub;
  try {
    sub = await fetch(SUBSCRIBE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name })
    });
  } catch (e) {
    console.error('otp-verify: subscribe call threw', String(e));
    return res.status(502).json({ ok: false, error: 'subscribe_failed' });
  }

  const raw = await sub.text().catch(() => '');
  const already = !sub.ok && /already subscribed/i.test(raw);
  if (!sub.ok && !already) {
    console.error('otp-verify: subscribe API', sub.status, raw);
    return res.status(502).json({ ok: false, error: 'subscribe_failed' });
  }

  // Already on the list: they still proved ownership, so report success — but do
  // not send a second welcome email promising a "first" digest.
  if (already) return res.status(200).json({ ok: true, already: true });

  const mail = await H.sendMail({
    to: email,
    subject: 'Thanks for subscribing to DigiVeritaz AI News',
    text: 'Hi ' + (name || 'there') + ',\n\n' +
          'Thanks for subscribing to DigiVeritaz AI News.\n\n' +
          'You will start getting the top digital marketing and AI news from the last 24 hours ' +
          'in your inbox from tomorrow at 10am IST.\n\n' +
          'Every edition has a one-click unsubscribe link, so you can stop any time.\n\n— DigiVeritaz',
    html: welcomeHtml(name)
  });

  // They ARE subscribed at this point. A failed welcome email must not be reported
  // as a failed subscription, or they will try again and hit "already subscribed".
  if (!mail.ok) console.error('otp-verify: welcome mail failed', mail.status, mail.detail);

  return res.status(200).json({ ok: true });
};

function welcomeHtml(name) {
  const who = name ? H.esc(name) : 'there';
  return '' +
  '<div style="font-family:Arial,Helvetica,sans-serif;max-width:520px;margin:0 auto;padding:24px;border:1px solid #e5e7eb;border-radius:12px">' +
    '<h2 style="color:#16a34a;margin:0 0 14px;font-size:20px">Thanks for subscribing</h2>' +
    '<p style="margin:0 0 12px">Hi ' + who + ',</p>' +
    '<p style="margin:0 0 12px">You are on the list for <strong>DigiVeritaz AI News</strong> — the top digital marketing and AI stories from the last 24 hours, summarised so you can read them in about three minutes.</p>' +
    '<div style="margin:22px 0;padding:16px 18px;background:#f0fdf4;border-left:4px solid #22c55e;border-radius:8px">' +
      '<strong>Your first edition arrives tomorrow at 10am IST.</strong>' +
    '</div>' +
    '<p style="color:#6b7280;font-size:13px;margin:0">Every edition has a one-click unsubscribe link, so you can stop any time.</p>' +
    '<p style="margin-top:18px">— The DigiVeritaz team</p>' +
  '</div>';
}
