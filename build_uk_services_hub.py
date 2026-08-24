#!/usr/bin/env python3
"""Create /uk/services/ from the India services hub.

/uk/services/ has to exist -- UK service pages now live beneath it, and a
directory with no index is a 404.

Derived from services/index.html so the chrome, layout and service grid
match the rest of the site, then adapted for the UK: en-GB, UK canonical,
hreflang pair, UK title/description. The five services that have real UK
pages point at /uk/services/<slug>/; the other 37 keep pointing at the
India pages, which is what the UK nav already does.

The BODY COPY IS STILL WRITTEN FOR INDIA -- 16 "India" mentions in the
prose. That needs a copywriter pass before this should be promoted.
"""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"
SRC = SITE / "services" / "index.html"
DST = SITE / "uk" / "services" / "index.html"

UK_LIVE = ["seo", "pay-per-click", "performance-marketing-agency",
           "paid-social-media-advertising", "generative-search-optimisation"]

TITLE = "Digital Marketing Services in the UK | DigiVeritaz"
DESC = ("Full-service digital marketing for UK brands — SEO, PPC, paid social, "
        "performance marketing and generative search optimisation.")

s = SRC.read_text(encoding="utf-8")

# locale
s = s.replace('<html lang="en-IN">', '<html lang="en-GB">')
s = s.replace('content="en_IN"', 'content="en_GB"')

# title / description / social
s = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", s, flags=re.S)
for pat in [r'(<meta name="description" content=")[^"]*"',
            r'(<meta property="og:description" content=")[^"]*"',
            r'(<meta name="twitter:description" content=")[^"]*"']:
    s = re.sub(pat, lambda m: m.group(1) + DESC + '"', s)
for pat in [r'(<meta property="og:title" content=")[^"]*"',
            r'(<meta name="twitter:title" content=")[^"]*"']:
    s = re.sub(pat, lambda m: m.group(1) + TITLE + '"', s)

# canonical + og:url -> UK
s = s.replace('href="https://www.digiveritaz.com/services/"',
              'href="https://www.digiveritaz.com/uk/services/"')
s = s.replace('content="https://www.digiveritaz.com/services/"',
              'content="https://www.digiveritaz.com/uk/services/"')

# hreflang block: mirror what the UK service pages use
s = re.sub(
    r'<link rel="alternate" hreflang="en-IN" href="[^"]*"/?>\s*'
    r'<link rel="alternate" hreflang="x-default" href="[^"]*"/?>',
    '<link rel="alternate" hreflang="en-GB" href="https://www.digiveritaz.com/uk/services/">\n'
    '<link rel="alternate" hreflang="en-IN" href="https://www.digiveritaz.com/services/">\n'
    '<link rel="alternate" hreflang="x-default" href="https://www.digiveritaz.com/">',
    s, count=1)

# the five with real UK pages point at their UK version
for slug in UK_LIVE:
    s = s.replace(f'href="/services/{slug}/"', f'href="/uk/services/{slug}/"')

DST.write_text(s, encoding="utf-8")
print(f"  wrote {DST.relative_to(SITE.parent)}  ({len(s):,} bytes)")
print(f"  UK-localised service links: {sum(s.count(f'/uk/services/{x}/') for x in UK_LIVE)}")
print(f'  remaining "India" mentions in copy: {s.count("India")}  <-- needs copywriter')
