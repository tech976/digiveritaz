#!/usr/bin/env python3
"""Phase 1 of the service-URL restructure: move 41 service pages under
/services/ and rewrite every reference to them.

Mapping comes from the SEO team's CSV verbatim. Two entries are not plain
moves -- the slug changes too:
    organic-marketing-services  -> organic-marketing
    whatsapp-marketing-services -> whatsapp-marketing

services.html also becomes services/index.html. A file and a directory
cannot both claim /services/, and the site already uses the directory
form for blog/ and case-study/ (there is no blog.html).

Rewrites are anchored on an opening quote or on the domain, so /uk/seo/
is never mistaken for /seo/.

This phase alone leaves the 41 OLD urls dead -- Phase 2 adds the 301s.
Do not deploy without it.
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

PAIRS = [
    ("seo", "seo"), ("social-media-management", "social-media-management"),
    ("influencer-marketing", "influencer-marketing"), ("digital-pr", "digital-pr"),
    ("online-reputation-management", "online-reputation-management"),
    ("organic-marketing-services", "organic-marketing"),
    ("whatsapp-marketing-services", "whatsapp-marketing"),
    ("performance-marketing-agency", "performance-marketing-agency"),
    ("ecommerce-marketing", "ecommerce-marketing"),
    ("generative-search-optimisation", "generative-search-optimisation"),
    ("pay-per-click", "pay-per-click"), ("display-advertising", "display-advertising"),
    ("facebook-instagram-advertising", "facebook-instagram-advertising"),
    ("shopping-ads", "shopping-ads"),
    ("paid-social-media-advertising", "paid-social-media-advertising"),
    ("amazon-marketing", "amazon-marketing"), ("native-advertising", "native-advertising"),
    ("ui-ux-design", "ui-ux-design"), ("product-design", "product-design"),
    ("branding-and-design", "branding-and-design"),
    ("communication-design", "communication-design"),
    ("content-copy-writing", "content-copy-writing"),
    ("conversion-rate-optimisation", "conversion-rate-optimisation"),
    ("revenue-generation", "revenue-generation"), ("lead-generation", "lead-generation"),
    ("cmo-consultancy", "cmo-consultancy"), ("landing-page-design", "landing-page-design"),
    ("real-estate-lead-generation", "real-estate-lead-generation"),
    ("research-and-insights", "research-and-insights"),
    ("strategy-and-planning", "strategy-and-planning"),
    ("analytics-configuration", "analytics-configuration"),
    ("google-tag-manager", "google-tag-manager"),
    ("data-strategy-consulting-services", "data-strategy-consulting-services"),
    ("website-development", "website-development"),
    ("custom-software-development", "custom-software-development"),
    ("ecommerce-development", "ecommerce-development"),
    ("wordpress-development", "wordpress-development"),
    ("mobile-app-development", "mobile-app-development"),
    ("linux-hosting", "linux-hosting"), ("business-email", "business-email"),
    ("crm-services", "crm-services"),
]
assert len(PAIRS) == 41 and len({o for o, _ in PAIRS}) == 41

TEXT_EXT = {".html", ".xml", ".json", ".txt", ".py", ".js"}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def move_files():
    moved = 0
    (SITE / "services").mkdir(exist_ok=True)
    # the hub page first: /services/ must keep working
    src, dst = SITE / "services.html", SITE / "services" / "index.html"
    if src.exists() and not dst.exists():
        r = git("mv", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)))
        if r.returncode: sys.exit(f"git mv services.html failed: {r.stderr}")
        print("  + services.html -> services/index.html")
        moved += 1
    for old, new in PAIRS:
        s, d = SITE / f"{old}.html", SITE / "services" / f"{new}.html"
        if not s.exists():
            print(f"  ! missing: {old}.html"); continue
        r = git("mv", str(s.relative_to(ROOT)), str(d.relative_to(ROOT)))
        if r.returncode: sys.exit(f"git mv {old} failed: {r.stderr}")
        moved += 1
    print(f"  moved {moved} files into site/services/")
    return moved


def rewrite_refs():
    # longest-first so 'organic-marketing-services' is matched before any prefix
    ordered = sorted(PAIRS, key=lambda p: -len(p[0]))
    alt = "|".join(re.escape(o) for o, _ in ordered)
    lookup = dict(ordered)

    # anchored on the opening quote, so /uk/seo/ can never match
    rel = re.compile(r'(?<=")/(%s)/' % alt)
    # anchored on the domain, same protection
    abso = re.compile(r'(digiveritaz\.com)/(%s)/' % alt)

    files = [p for p in ROOT.rglob("*")
             if p.is_file() and p.suffix in TEXT_EXT
             and ".git" not in p.parts and p.name != Path(__file__).name]

    tot_r = tot_a = tot_f = 0
    for p in files:
        try:
            t = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            continue
        new, nr = rel.subn(lambda m: "/services/%s/" % lookup[m.group(1)], t)
        new, na = abso.subn(lambda m: "%s/services/%s/" % (m.group(1), lookup[m.group(2)]), new)
        if nr or na:
            p.write_text(new, encoding="utf-8")
            tot_r += nr; tot_a += na; tot_f += 1
    print(f"  rewrote {tot_r:,} relative + {tot_a:,} absolute refs across {tot_f} files")


if __name__ == "__main__":
    print("== moving files ==");      move_files()
    print("== rewriting references =="); rewrite_refs()
