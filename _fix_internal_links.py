#!/usr/bin/env python3
"""Convert every relative internal page link from
   href="something.html"        -> href="/something/"
   href="something.html#frag"   -> href="/something/#frag"
   href="index.html"            -> href="/"
   href="index.html#frag"       -> href="/#frag"
across all HTML files in site/, plus build.py.

External links (https://…, http://…, mailto:, tel:) are untouched.
"""
import pathlib, re

SITE = pathlib.Path(__file__).resolve().parent / "site"

# Build the set of internal .html filenames we own (basenames, no extension).
html_files = sorted(p.name for p in SITE.glob("*.html"))
print(f"Found {len(html_files)} HTML files in site/")

# Regex: href="<filename>.html"   OR  href="<filename>.html#frag"
# - filename has no slash and no "://" so it's relative
# - capture frag (#…) optionally
LINK_RE = re.compile(
    r'href="(?P<base>[^"/?#:]+)\.html(?P<frag>#[^"]*)?"'
)

def fix(m: re.Match) -> str:
    base = m.group("base")
    frag = m.group("frag") or ""
    if base == "index":
        return f'href="/{frag}"'
    return f'href="/{base}/{frag}"'

targets = list(SITE.glob("*.html")) + [SITE / "build.py"]
total_changed = 0
total_subs = 0
for p in targets:
    if not p.is_file():
        continue
    src = p.read_text(encoding="utf-8")
    new, n = LINK_RE.subn(fix, src)
    if n:
        p.write_text(new, encoding="utf-8")
        total_changed += 1
        total_subs += n
        print(f"  ✓ {p.name}: {n} links rewritten")

print(f"\nTotal: {total_changed} files updated, {total_subs} internal links rewritten.")
