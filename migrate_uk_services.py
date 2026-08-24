#!/usr/bin/env python3
"""Mirror the India /services/ structure onto the UK pages.

The 5 UK service pages sit flat at /uk/<slug>/ while India now uses
/services/<slug>/. The brief asks for /uk/services/, so UK follows the
same shape: /uk/services/<slug>/.

Only the 5 pages that already exist are moved. Nothing is duplicated --
creating UK copies of the other 37 services, 163 blog posts and 25 case
studies is a content decision, not a mechanical one.
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
UK = SITE / "uk"

SLUGS = ["seo", "pay-per-click", "performance-marketing-agency",
         "paid-social-media-advertising", "generative-search-optimisation"]

def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)

# --- move the 5 pages ---
(UK / "services").mkdir(exist_ok=True)
moved = 0
for s in SLUGS:
    src, dst = UK / f"{s}.html", UK / "services" / f"{s}.html"
    if not src.exists():
        print(f"  ! missing uk/{s}.html"); continue
    r = git("mv", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)))
    if r.returncode: sys.exit(f"git mv failed: {r.stderr}")
    moved += 1
print(f"  moved {moved} UK service pages -> uk/services/")

# --- rewrite every reference /uk/<slug>/ -> /uk/services/<slug>/ ---
alt = "|".join(map(re.escape, SLUGS))
rel  = re.compile(r'(?<=")/uk/(%s)/' % alt)
abso = re.compile(r'(digiveritaz\.com)/uk/(%s)/' % alt)

tot_r = tot_a = files = 0
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix not in {".html", ".xml", ".json", ".txt", ".py", ".js"}:
        continue
    if ".git" in p.parts or p.name == Path(__file__).name:
        continue
    try: t = p.read_text(encoding="utf-8")
    except Exception: continue
    n, nr = rel.subn(lambda m: "/uk/services/%s/" % m.group(1), t)
    n, na = abso.subn(lambda m: "%s/uk/services/%s/" % (m.group(1), m.group(2)), n)
    if nr or na:
        p.write_text(n, encoding="utf-8"); tot_r += nr; tot_a += na; files += 1
print(f"  rewrote {tot_r} relative + {tot_a} absolute refs across {files} files")
