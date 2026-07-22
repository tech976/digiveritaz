/* GET /api/unsubscribe?token=...  ->  proxies the digest service's unsubscribe page
 *
 * The digest service builds its unsubscribe links from APP_URL, which is set to
 * https://digiveritaz.com — so every link in every edition points at
 * digiveritaz.com/api/unsubscribe?token=... But Cloudflare routes /api/* on this
 * domain to THIS Vercel project, which had no such route, so every unsubscribe
 * link 404d. A newsletter with dead unsubscribe links is both a spam-complaint
 * magnet and a legal problem (DPDP in India, GDPR/CAN-SPAM for overseas readers).
 *
 * Proxying rather than redirecting keeps the branded domain in the address bar and
 * means the fix holds even if APP_URL is corrected later — this route simply stops
 * being hit. Only the token is forwarded, to a hard-coded upstream, so this cannot
 * be turned into an open proxy.
 */
const UPSTREAM = process.env.UNSUBSCRIBE_UPSTREAM ||
  'https://email-automation-blond-nine.vercel.app/api/unsubscribe';

function page(title, message) {
  return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<meta name="robots" content="noindex"><title>' + title + '</title></head>' +
    '<body style="font-family:Inter,Arial,sans-serif;background:#0c0f1f;color:#eceef6;' +
    'display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0">' +
    '<div style="text-align:center;max-width:420px;padding:24px">' +
    '<h1 style="font-size:1.3rem;margin:0 0 10px">' + title + '</h1>' +
    '<p style="color:#9aa3b8;line-height:1.6;margin:0 0 20px">' + message + '</p>' +
    '<a href="https://www.digiveritaz.com/ai-news/" style="color:#22c55e">Back to DigiVeritaz AI News</a>' +
    '</div></body></html>';
}

module.exports = async (req, res) => {
  try {
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.setHeader('Allow', 'GET, HEAD');
      return res.status(405).send(page('Not allowed', 'Open your unsubscribe link directly from the email.'));
    }

    const token = String((req.query && req.query.token) || '').trim();
    if (!token || token.length > 512 || !/^[A-Za-z0-9._~-]+$/.test(token)) {
      return res.status(400).send(page('Link not recognised',
        'This unsubscribe link is invalid or has already been used.'));
    }

    const r = await fetch(UPSTREAM + '?token=' + encodeURIComponent(token), {
      method: 'GET',
      headers: { 'User-Agent': 'digiveritaz-unsubscribe-proxy' },
      redirect: 'follow'
    });
    const body = await r.text();

    res.setHeader('Content-Type', r.headers.get('content-type') || 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Robots-Tag', 'noindex');
    return res.status(r.status).send(body);
  } catch (e) {
    console.error('unsubscribe proxy failed:', e && e.stack ? e.stack : e);
    // Never leave someone stuck on a dead page when they are trying to opt out.
    return res.status(200).send(page('We could not complete that just now',
      'Please try the link again in a minute, or email ' +
      '<a href="mailto:info@digiveritaz.com?subject=Unsubscribe%20from%20AI%20News" ' +
      'style="color:#22c55e">info@digiveritaz.com</a> and we will remove you.'));
  }
};
