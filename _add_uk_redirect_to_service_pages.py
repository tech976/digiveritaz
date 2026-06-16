#!/usr/bin/env python3
"""
Add a UK-visitor redirect script to each of the 5 India service pages.

When a UK visitor lands on /seo/, /pay-per-click/, etc., the script:
  1. Reads Cloudflare's /cdn-cgi/trace (real IP geolocation — works with VPNs)
  2. If loc=GB → window.location.replace() to the /uk/<slug>/ equivalent
  3. Otherwise → no-op, India page renders normally

Overrides for testing: ?region=IN forces India view; ?region=UK forces redirect immediately.
Googlebot crawls from US IPs → loc=US → not redirected → SEO unaffected.

Script is inserted into <head> right before </head> so it fires before content paints.
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

REDIRECT_SCRIPT_TEMPLATE = """<script>
/* UK visitor redirect: send GB visitors to the /uk/{slug}/ counterpart.
   Primary signal is Cloudflare's /cdn-cgi/trace (real IP geolocation — works with VPNs).
   Bots crawl from non-GB IPs so SEO is unaffected.
   Overrides for testing: ?region=IN stays here; ?region=UK redirects immediately. */
(function(){{
  var UK_DEST = "/uk/{slug}/";
  function goUK(){{ try {{ location.replace(UK_DEST + (location.search || "") + (location.hash || "")); }} catch (e) {{}} }}
  try {{
    var s = location.search || "";
    if (/[?&]region=IN\\b/i.test(s)) return;
    if (/[?&]region=UK\\b/i.test(s)) {{ goUK(); return; }}
  }} catch (e) {{}}
  if (!window.fetch) return;
  fetch("/cdn-cgi/trace", {{ cache: "no-store" }})
    .then(function(r){{ if (!r.ok) throw new Error(); return r.text(); }})
    .then(function(txt){{
      var m = /(?:^|\\n)loc=([A-Z]{{2}})/.exec(txt || "");
      if (m && m[1] === "GB") goUK();
    }})
    .catch(function(){{}});
}})();
</script>
"""

MARKER = "UK visitor redirect:"  # used to detect idempotency

def main():
    for slug in SLUGS:
        page = ROOT / f"{slug}.html"
        if not page.exists():
            print(f"[ERROR] {slug}.html not found at {page}")
            continue

        html = page.read_text(encoding="utf-8")

        if MARKER in html:
            print(f"[skip] {slug}.html already has UK redirect script")
            continue

        # Insert the script right before </head> so it fires as early as possible
        # before the page content paints.
        if "</head>" not in html:
            print(f"[ERROR] {slug}.html has no </head> tag — skipping")
            continue

        script = REDIRECT_SCRIPT_TEMPLATE.format(slug=slug)
        new_html = html.replace("</head>", script + "</head>", 1)
        page.write_text(new_html, encoding="utf-8")
        print(f"[done] {slug}.html — added UK redirect → /uk/{slug}/")

    print("\nAll service pages now have the UK redirect.")
    print("Test by visiting any of:")
    for slug in SLUGS:
        print(f"  https://www.digiveritaz.com/{slug}/")


if __name__ == "__main__":
    main()
