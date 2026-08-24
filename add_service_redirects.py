#!/usr/bin/env python3
"""Phase 2: 301 the 41 old flat service URLs to their new /services/ paths.

Sources use the trailing-slash form to match the redirects already in this
file, and because trailingSlash is true, Vercel normalises /seo -> /seo/
before these fire.

The existing apex->www catch-all is scoped with a host condition, so it
does not shadow these. The /blog-:slug/ style patterns are prefix matches
that cannot collide with these exact paths.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = ROOT / "site" / "vercel.json"

RENAME = {"organic-marketing-services": "organic-marketing",
          "whatsapp-marketing-services": "whatsapp-marketing"}

SLUGS = [
    "seo", "social-media-management", "influencer-marketing", "digital-pr",
    "online-reputation-management", "organic-marketing-services",
    "whatsapp-marketing-services", "performance-marketing-agency",
    "ecommerce-marketing", "generative-search-optimisation", "pay-per-click",
    "display-advertising", "facebook-instagram-advertising", "shopping-ads",
    "paid-social-media-advertising", "amazon-marketing", "native-advertising",
    "ui-ux-design", "product-design", "branding-and-design",
    "communication-design", "content-copy-writing", "conversion-rate-optimisation",
    "revenue-generation", "lead-generation", "cmo-consultancy",
    "landing-page-design", "real-estate-lead-generation", "research-and-insights",
    "strategy-and-planning", "analytics-configuration", "google-tag-manager",
    "data-strategy-consulting-services", "website-development",
    "custom-software-development", "ecommerce-development", "wordpress-development",
    "mobile-app-development", "linux-hosting", "business-email", "crm-services",
]
assert len(SLUGS) == 41 and len(set(SLUGS)) == 41

cfg = json.loads(CFG.read_text(encoding="utf-8"))
existing = {r["source"] for r in cfg["redirects"]}

added = 0
for slug in SLUGS:
    src = f"/{slug}/"
    if src in existing:
        print(f"  = already redirected: {src}")
        continue
    cfg["redirects"].append({
        "source": src,
        "destination": f"/services/{RENAME.get(slug, slug)}/",
        "permanent": True,
    })
    added += 1

CFG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
print(f"\n  added {added} redirects | total now {len(cfg['redirects'])}")
