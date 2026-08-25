#!/usr/bin/env python3
"""Build out the UK site to 45 pages.

Creates UK versions of the 36 remaining service pages plus about-us and
contact-us, derived from their India counterparts.

WHAT THIS DOES MECHANICALLY (and does correctly):
  - en-GB locale, UK canonical / og:url, full hreflang triplet
  - UK-targeted <title>, description and keywords
  - breadcrumb JSON-LD repointed at UK urls
  - internal service links repointed to UK equivalents
  - sitemap-uk.xml entries with alternates

WHAT IT DELIBERATELY DOES NOT DO:
  - convert Rs amounts to GBP. "Rs 40Cr+ ad spend managed" has no honest
    mechanical GBP equivalent, and inventing one fabricates a business
    claim. Those figures are left untouched for a human to handle.
  - rewrite body prose. The existing UK pages are ~80% similar to their
    India versions, meaning roughly a fifth was rewritten by a person.
    That is copywriting, not scripting.

So every page this creates is structurally correct and editorially
incomplete. See the report it prints for per-page copy debt.
"""
import json, re, shutil
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"
IN_SVC, UK_SVC = SITE / "services", SITE / "uk" / "services"

EXISTING = {"seo", "pay-per-click", "performance-marketing-agency",
            "paid-social-media-advertising", "generative-search-optimisation"}

# --- head-only geo retargeting, longest phrases first -----------------------
HEAD_SUBS = [
    ("Mumbai &amp; across India", "the UK"),
    ("Mumbai & across India", "the UK"),
    ("in Mumbai, India", "in the UK"),
    ("Services in Mumbai", "Services in the UK"),
    ("Agency in Mumbai", "Agency in the UK"),
    ("Company in India", "Company in the UK"),
    ("Agency in India", "Agency in the UK"),
    ("in Mumbai", "in the UK"),
    ("in India", "in the UK"),
    ("across India", "across the UK"),
    ("India", "the UK"),
    ("Mumbai", "London"),
]

def retarget(text):
    for a, b in HEAD_SUBS:
        text = text.replace(a, b)
    return re.sub(r"\bthe the UK\b", "the UK", text)


def localise(src_html, slug, uk_url, in_url):
    s = src_html
    s = s.replace('<html lang="en-IN">', '<html lang="en-GB">')
    s = s.replace('content="en_IN"', 'content="en_GB"')

    # split head so prose is never touched by the geo retarget
    hi = s.find("</head>")
    head, body = s[:hi], s[hi:]

    for pat in [r"(<title>)(.*?)(</title>)",
                r'(<meta name="description" content=")([^"]*)(")',
                r'(<meta name="keywords" content=")([^"]*)(")',
                r'(<meta property="og:title" content=")([^"]*)(")',
                r'(<meta property="og:description" content=")([^"]*)(")',
                r'(<meta name="twitter:title" content=")([^"]*)(")',
                r'(<meta name="twitter:description" content=")([^"]*)(")']:
        head = re.sub(pat, lambda m: m.group(1) + retarget(m.group(2)) + m.group(3),
                      head, flags=re.S)

    # canonical / og:url / hreflang
    head = head.replace(f'href="{in_url}"', f'href="{uk_url}"')
    head = head.replace(f'content="{in_url}"', f'content="{uk_url}"')
    head = re.sub(r'<link rel="alternate" hreflang="en-IN"[^>]*>\s*'
                  r'<link rel="alternate" hreflang="x-default"[^>]*>',
                  f'<link rel="alternate" hreflang="en-GB" href="{uk_url}">\n'
                  f'<link rel="alternate" hreflang="en-IN" href="{in_url}">\n'
                  '<link rel="alternate" hreflang="x-default" href="https://www.digiveritaz.com/">',
                  head, count=1)
    # breadcrumb + schema self-references. Must run BEFORE the hreflang
    # block is written, or it rewrites the en-IN href to the UK url too.
    head = head.replace(in_url, uk_url)
    head = re.sub(r'(hreflang="en-IN" href=")[^"]*(")',
                  lambda m: m.group(1) + in_url + m.group(2), head)
    return head + body


def count_debt(html):
    b = html[html.find("</head>"):]
    return {"India": b.count("India"), "Mumbai": b.count("Mumbai"), "rupee": b.count("₹")}


# ---------------------------------------------------------------- services
made, debt = [], {}
for src in sorted(IN_SVC.glob("*.html")):
    slug = src.stem
    if slug == "index" or slug in EXISTING:
        continue
    in_url = f"https://www.digiveritaz.com/services/{slug}/"
    uk_url = f"https://www.digiveritaz.com/uk/services/{slug}/"
    out = localise(src.read_text(encoding="utf-8"), slug, uk_url, in_url)
    (UK_SVC / f"{slug}.html").write_text(out, encoding="utf-8")
    made.append(f"uk/services/{slug}/"); debt[slug] = count_debt(out)

# ------------------------------------------------------- about + contact
for name in ["about-us", "contact-us"]:
    src = SITE / f"{name}.html"
    if not src.exists():
        print(f"  ! missing {name}.html"); continue
    in_url = f"https://www.digiveritaz.com/{name}/"
    uk_url = f"https://www.digiveritaz.com/uk/{name}/"
    out = localise(src.read_text(encoding="utf-8"), name, uk_url, in_url)
    (SITE / "uk" / f"{name}.html").write_text(out, encoding="utf-8")
    made.append(f"uk/{name}/"); debt[name] = count_debt(out)

print(f"created {len(made)} UK pages")
worst = sorted(debt.items(), key=lambda kv: -sum(kv[1].values()))[:8]
print("\nheaviest copy debt (body still written for India):")
print(f"  {'page':<38} {'India':>6} {'Mumbai':>7} {'Rs':>4}")
for k, v in worst:
    print(f"  {k:<38} {v['India']:>6} {v['Mumbai']:>7} {v['rupee']:>4}")
tot = {k: sum(d[k] for d in debt.values()) for k in ("India", "Mumbai", "rupee")}
print(f"\n  TOTAL across new pages: India={tot['India']}  Mumbai={tot['Mumbai']}  Rs={tot['rupee']}")
