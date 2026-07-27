#!/usr/bin/env python3
"""Fix oversized Ask-AI icons on the live site.

Two causes, both fixed here:

1. The inline <svg>s carried no width/height, so any moment the CSS is not
   in effect (stale CDN copy, first paint before the stylesheet lands) they
   fall back to the SVG default of 300x150 and render enormous. Explicit
   attributes make them correct with no CSS at all.

2. The stylesheets are cache-busted with ?v=<n> in every <link>. The new
   .askai-btn rules were appended without bumping that number, so browsers
   and the CDN kept serving the old CSS. Bumped below.

Only the markup inside .foot-askai is touched -- the same <svg ...> opener
appears on other icons elsewhere on the page.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

NEW_VER = "1785700000"
# bundles that received the .askai-btn rules
BUMP = ["style.min.css", "home-bundle.min.css", "home-dark.min.css", "home.min.css"]

BLOCK_RE = re.compile(r'<div class="foot-askai">.*?</div>\s*</div>', re.S)
SVG_OPEN_RE = re.compile(r'<svg (?!width=)')


def fix_block(m):
    return SVG_OPEN_RE.sub('<svg width="26" height="26" ', m.group(0))


def main():
    icons = vers = 0
    for p in sorted(SITE.rglob("*.html")) + [SITE / "build.py"]:
        if not p.is_file():
            continue
        src = p.read_text(encoding="utf-8")
        new = BLOCK_RE.sub(fix_block, src)
        if new != src:
            icons += 1

        before = new
        for name in BUMP:
            new = re.sub(
                r"(css/" + re.escape(name) + r"\?v=)\d+", r"\g<1>" + NEW_VER, new
            )
        if new != before:
            vers += 1

        if new != src:
            p.write_text(new, encoding="utf-8")

    print(f"icon dimensions added in : {icons} files")
    print(f"css cache-buster bumped  : {vers} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
