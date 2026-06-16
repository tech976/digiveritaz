#!/usr/bin/env python3
"""
Wire up hreflang reciprocity for the 5 UK service pages:
  1. Add <link rel="alternate" hreflang="en-GB"> to each India source page
  2. Add the 5 new UK URLs to sitemap-uk.xml (with hreflang annotations)
  3. Add xhtml:link hreflang annotations to the 5 corresponding entries in sitemap-in.xml
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent / "site"
SLUGS = [
    "seo",
    "pay-per-click",
    "performance-marketing-agency",
    "paid-social-media-advertising",
    "generative-search-optimisation",
]

# 1) Add en-GB hreflang to each India service page (insert after the en-IN line if not already present)
for slug in SLUGS:
    page = ROOT / f"{slug}.html"
    html = page.read_text(encoding="utf-8")
    en_gb_link = f'<link rel="alternate" hreflang="en-GB" href="https://www.digiveritaz.com/uk/{slug}/">'

    if en_gb_link in html:
        print(f"[skip] {slug}.html already has en-GB hreflang")
        continue

    en_in_line = f'<link rel="alternate" hreflang="en-IN" href="https://www.digiveritaz.com/{slug}/">'
    if en_in_line not in html:
        print(f"[ERROR] {slug}.html missing expected en-IN line; skipping")
        continue

    html = html.replace(en_in_line, en_in_line + "\n" + en_gb_link, 1)
    page.write_text(html, encoding="utf-8")
    print(f"[done] {slug}.html — added en-GB hreflang")

# 2) Update sitemap-uk.xml: add the 5 new UK URLs with hreflang annotations
sitemap_uk = ROOT / "sitemap-uk.xml"
existing = sitemap_uk.read_text(encoding="utf-8")
url_entries = ""
for slug in SLUGS:
    url_entries += f"""
  <url>
    <loc>https://www.digiveritaz.com/uk/{slug}/</loc>
    <lastmod>2026-06-15</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
    <xhtml:link rel="alternate" hreflang="en-GB" href="https://www.digiveritaz.com/uk/{slug}/"/>
    <xhtml:link rel="alternate" hreflang="en-IN" href="https://www.digiveritaz.com/{slug}/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://www.digiveritaz.com/"/>
  </url>
"""

# Insert before </urlset>
if any(slug + "/</loc>" in existing for slug in SLUGS):
    print("[skip] sitemap-uk.xml already has UK service URLs (or duplicates would result)")
else:
    new_xml = existing.replace("</urlset>", url_entries + "</urlset>")
    sitemap_uk.write_text(new_xml, encoding="utf-8")
    print(f"[done] sitemap-uk.xml — added {len(SLUGS)} UK service URLs")

# 3) Update sitemap-in.xml: add hreflang annotations on the 5 India service entries
sitemap_in = ROOT / "sitemap-in.xml"
sitemap_in_xml = sitemap_in.read_text(encoding="utf-8")

for slug in SLUGS:
    # The India service entries in the current sitemap-in.xml use a one-line compact format:
    # <url><loc>https://www.digiveritaz.com/<slug>/</loc><lastmod>...</lastmod>...</url>
    # We need to find that exact pattern for this slug and append xhtml:link tags before </url>.

    # Match the existing compact entry for this slug
    compact_pattern = re.compile(
        r"(<url><loc>https://www\.digiveritaz\.com/" + re.escape(slug) + r"/</loc>[^<]*<lastmod>[^<]*</lastmod>[^<]*<changefreq>[^<]*</changefreq>[^<]*<priority>[^<]*</priority>)</url>"
    )
    match = compact_pattern.search(sitemap_in_xml)
    if not match:
        print(f"[ERROR] sitemap-in.xml — no compact entry found for /{slug}/")
        continue

    # Skip if already annotated
    if f'href="https://www.digiveritaz.com/uk/{slug}/"' in sitemap_in_xml:
        print(f"[skip] sitemap-in.xml — /{slug}/ already has hreflang annotation")
        continue

    annotation = (
        f'<xhtml:link rel="alternate" hreflang="en-IN" href="https://www.digiveritaz.com/{slug}/"/>'
        f'<xhtml:link rel="alternate" hreflang="en-GB" href="https://www.digiveritaz.com/uk/{slug}/"/>'
        f'<xhtml:link rel="alternate" hreflang="x-default" href="https://www.digiveritaz.com/{slug}/"/>'
    )
    replacement = match.group(1) + annotation + "</url>"
    sitemap_in_xml = sitemap_in_xml.replace(match.group(0), replacement, 1)
    print(f"[done] sitemap-in.xml — added hreflang annotation for /{slug}/")

sitemap_in.write_text(sitemap_in_xml, encoding="utf-8")

print("\nAll linking complete.")
