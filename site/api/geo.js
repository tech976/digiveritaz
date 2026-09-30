/* GET /api/geo  ->  { ok:true, city, region, country, country_code, src }
 *
 * Approximate visitor location for lead attribution (city / state / country), as
 * estimated from the IP address by the CDN. No browser location prompt, no GPS, and
 * the IP address itself is never returned or stored. Disclosed in the privacy policy.
 *
 * Cloudflare sits in front of Vercel, so Vercel's own x-vercel-ip-* headers describe
 * the Cloudflare server that connected to Vercel, not the visitor. They are used only
 * when the request did not come through Cloudflare (e.g. the *.vercel.app URL).
 * CF-IPCountry is on by default; cf-ipcity / cf-region need Cloudflare's
 * "Add visitor location headers" Managed Transform.
 */
function utf8(v) {
  // Node exposes raw header bytes as latin1; Cloudflare sends city names as UTF-8.
  return Buffer.from(String(v || ''), 'latin1').toString('utf8').trim();
}
function uri(v) {
  // Vercel URL-encodes x-vercel-ip-city ("New%20Delhi").
  try { return decodeURIComponent(String(v || '')).trim(); } catch (e) { return String(v || '').trim(); }
}
function countryName(code) {
  try { return new Intl.DisplayNames(['en'], { type: 'region' }).of(code) || code; } catch (e) { return code; }
}

module.exports = (req, res) => {
  const h = req.headers || {};
  let city = '', region = '', code = '', src = 'none';

  if (h['cf-ray']) {
    city = utf8(h['cf-ipcity']);
    region = utf8(h['cf-region']);
    code = utf8(h['cf-ipcountry']).toUpperCase();
    src = 'cloudflare';
  } else if (h['x-vercel-ip-country']) {
    city = uri(h['x-vercel-ip-city']);
    region = uri(h['x-vercel-ip-country-region']);
    code = uri(h['x-vercel-ip-country']).toUpperCase();
    src = 'vercel';
  }
  if (!/^[A-Z]{2}$/.test(code) || code === 'XX' || code === 'T1') code = '';  // XX unknown, T1 Tor

  res.setHeader('Cache-Control', 'private, no-store, max-age=0');
  res.setHeader('CDN-Cache-Control', 'no-store');
  res.setHeader('Vercel-CDN-Cache-Control', 'no-store');
  res.status(200).json({
    ok: true,
    city: city.slice(0, 80),
    region: region.slice(0, 80),
    country: code ? countryName(code) : '',
    country_code: code,
    src: src
  });
};
