#!/usr/bin/env python3
"""Bump ?v= on main.min.js so visitors actually fetch the UTM fix.

main.min.js stopped appending the stored campaign (utm_*/gclid/fbclid) to
internal links, but every page still asked for ?v=1791010000. Browsers and
the CDN both key their cache on the full URL, so that unchanged query string
kept serving the previous bundle -- /services/.../ went on handing out
?utm_source=facebook&utm_medium=paid_social on every internal click even
though the deployed file no longer contained the code that did it.
"""
from pathlib import Path
import re

SITE = Path(__file__).resolve().parents[2] / "site"
OLD_VER = "1791010000"
NEW_VER = "1791020000"

pat = re.compile(r"(/js/main\.min\.js\?v=)\d+")
bumped = files = 0
for p in sorted(SITE.rglob("*.html")):
    src = p.read_text(encoding="utf-8")
    new, n = pat.subn(r"\g<1>" + NEW_VER, src)
    if n:
        p.write_text(new, encoding="utf-8")
        files += 1
        bumped += n
print(f"bumped {bumped} reference(s) across {files} page(s): {OLD_VER} -> {NEW_VER}")
