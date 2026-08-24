#!/usr/bin/env python3
"""Stamp today's date on the 42 relocated service URLs.

They moved to brand-new paths today but still claimed lastmod 2026-05-20.
Google leans on lastmod to decide what to recrawl, and a new URL asserting
it was last changed three months ago slows discovery of the migration
exactly when it needs to be fast.

Also refreshes the two lastmod values in the sitemap index, since both
child sitemaps changed today.
"""
import re
from pathlib import Path

TODAY = "2026-08-24"
SITE = Path(__file__).resolve().parent / "site"

# --- child sitemap: only the /services/ entries ---
p = SITE / "sitemap-in.xml"
s = p.read_text(encoding="utf-8")
block = re.compile(
    r"(<url>\s*<loc>https://www\.digiveritaz\.com/services/[^<]*</loc>\s*<lastmod>)([^<]+)(</lastmod>)"
)
s, n = block.subn(lambda m: m.group(1) + TODAY + m.group(3), s)
p.write_text(s, encoding="utf-8")
print(f"  sitemap-in.xml : {n} service entries stamped {TODAY}")

# --- sitemap index: both children changed today ---
p = SITE / "sitemap.xml"
s = p.read_text(encoding="utf-8")
s, n = re.subn(r"(<lastmod>)\d{4}-\d{2}-\d{2}(</lastmod>)",
               lambda m: m.group(1) + TODAY + m.group(2), s)
p.write_text(s, encoding="utf-8")
print(f"  sitemap.xml    : {n} index lastmod values refreshed")

# --- uk sitemap: its hreflang alternates were rewritten today ---
p = SITE / "sitemap-uk.xml"
s = p.read_text(encoding="utf-8")
s, n = re.subn(r"(<lastmod>)\d{4}-\d{2}-\d{2}(</lastmod>)",
               lambda m: m.group(1) + TODAY + m.group(2), s)
p.write_text(s, encoding="utf-8")
print(f"  sitemap-uk.xml : {n} entries refreshed")
