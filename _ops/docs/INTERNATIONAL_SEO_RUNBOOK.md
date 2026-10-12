# International SEO — UK Market Setup

This is the operations runbook for the international/UK SEO work. It covers what
was done in code and what still has to be done by hand in Google Search Console.

## What was done in code

- `site/uk/index.html` — UK-localized homepage (title, meta description,
  keywords, OG, Twitter, schema, H1, hreflang, canonical, `lang="en-GB"`).
- `site/index.html` — added `hreflang="en-GB"` pointing to `/uk/` (en-IN +
  x-default were already present).
- `site/sitemap-in.xml` — copy of the original sitemap (India URLs) with
  hreflang annotations on the homepage entry.
- `site/sitemap-uk.xml` — new sitemap with the `/uk/` URL and matching
  hreflang annotations.
- `site/sitemap.xml` — rewritten as a sitemap **index** pointing at both market
  sitemaps. Existing GSC registration of `sitemap.xml` will keep working — GSC
  auto-detects the index format and fetches the children.
- `site/robots.txt` — now lists all three sitemap URLs (index + each market).

## Manual steps that have to be done in Google Search Console (GSC)

GSC settings are per-property in the Search Console UI. There is no public API
for these — they have to be clicked through by a human with property access.

### 1. Submit the new sitemaps

GSC → property `https://www.digiveritaz.com/` → **Sitemaps** (left nav).

- Existing `sitemap.xml` entry should auto-re-read as a sitemap index after
  the next crawl. To force it, click the existing entry, "Remove sitemap",
  then resubmit `sitemap.xml`.
- Add new entry: `sitemap-in.xml`.
- Add new entry: `sitemap-uk.xml`.

Expected within 24–72h: all three show "Success" with non-zero "Discovered URLs"
(81 for `sitemap-in.xml`, 1 for `sitemap-uk.xml`).

### 2. International Targeting (only if a legacy property is in use)

Note: Google **retired** the "International Targeting" → "Country" setting in
Search Console in mid-2022 for new Domain properties. Country targeting is now
inferred from hreflang + ccTLD + IP signals.

If — and only if — the property is a legacy URL-prefix property AND the
"Legacy tools and reports" → "International Targeting" link still appears in
the left nav:

- GSC → property → Legacy tools → **International Targeting** → **Country** tab.
- Set the **root property** target to **India** (matches the en-IN canonical at
  `/`).
- Do NOT also target the root property to UK — that would conflict with the
  hreflang signal pointing UK users to `/uk/`.

If you want a separate UK target signal in GSC, the supported way today is to
add `https://www.digiveritaz.com/uk/` as its **own** URL-prefix property in
GSC, verify ownership, then submit `sitemap-uk.xml` from inside that property.
This also gives you per-market performance reports (impressions/clicks broken
out for `/uk/`), which is the practical reason to do it.

### 3. Verify hreflang is being picked up

GSC → property → **Search results** report → filter by query/URL — wait ~1 week
after deploy for data to accumulate. Then:

- GSC → Legacy tools → **International Targeting** → **Language** tab — should
  show hreflang tags with **no errors** ("Tagged page has no return tag" is the
  most common one we're avoiding by making the en-IN ↔ en-GB pair reciprocal).
- Or run [hreflang.org's validator](https://hreflang.org/) against
  `https://www.digiveritaz.com/` and `https://www.digiveritaz.com/uk/` —
  both should show clean.

### 4. Optional but recommended: Screaming Frog audit

Screaming Frog (desktop crawler) → Configuration → Spider → "Crawl Linked
hreflang URLs" enabled → crawl `https://www.digiveritaz.com/`.

Look for:
- **Hreflang** tab → all `en-IN`/`en-GB`/`x-default` rows green ✓.
- **"Missing Return Links"** report empty.
- **"Inconsistent Language and Country Codes"** empty.

## Future expansion

When more pages get UK versions (service pages, case studies, blog):

1. Create `site/uk/<page>.html` with the same head pattern (canonical, hreflang
   pair, en_GB locale).
2. Add the matching `<xhtml:link rel="alternate" hreflang="en-GB"/>` annotation
   to the corresponding en-IN entry in `sitemap-in.xml`.
3. Add the new entry to `sitemap-uk.xml`.
4. Add the matching `hreflang="en-GB"` link in the en-IN page's `<head>`.

Hreflang must be **reciprocal** — every page that says "my en-GB alternate is X"
must be matched by X saying "my en-IN alternate is back here". This is the most
common source of GSC hreflang errors.
