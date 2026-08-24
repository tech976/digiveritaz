#!/usr/bin/env python3
"""
C15 — Route UK visitors from /uk/index.html nav to /uk/<slug>/ directly
(instead of bouncing off /seo/ etc. via the redirect script).

Updates:
  1. 5 mega-menu links → /uk/<slug>/
  2. 3 footer "Services" list links → /uk/<slug>/
  3. 1 static preview CTA href (the default-shown "Explore SEO Services")
  4. Inserts an inline override script before </body> that intercepts
     the dynamic wwd-row clicks (which home.min.js wires to relative URLs)
     and forces them to absolute URLs — /uk/<slug>/ for the 3 services with
     UK pages (seo, paid, perf), /<slug>/ for the 3 without (ecom, wa, brand).
"""
from pathlib import Path

PAGE = Path(__file__).parent / "site" / "uk" / "index.html"

# Top-5 audit priority — these have UK pages, so links should go to /uk/<slug>/
UK_LINK_UPDATES = [
    ("seo",                              "SEO"),
    ("pay-per-click",                    "Search PPC"),
    ("performance-marketing-agency",     "Performance Marketing"),
    ("paid-social-media-advertising",    "Social Media Advertising"),
    ("generative-search-optimisation",   "Generative Engine Optimisation"),
]

# Footer Services list — only 3 of our top-5 appear there
FOOTER_LINK_UPDATES = [
    ("seo",                              "SEO"),
    ("pay-per-click",                    "Pay Per Click"),
    ("performance-marketing-agency",     "Performance Marketing"),
]

# Inline override script for wwd-row dynamic preview clicks
WWD_OVERRIDE_SCRIPT = """<script>
/* C15 — Force wwd-row clicks + preview CTA to absolute URLs.
   home.min.js wires service rows to relative URLs (e.g. "seo.html") which on
   /uk/ resolve to /uk/seo.html → 404 for services without a UK page.
   Solution: capture-phase click handler that uses absolute URLs and a
   MutationObserver that fixes the CTA href whenever the preview re-renders. */
(function(){
  var MAP = {
    "seo":   "/uk/services/seo/",
    "paid":  "/uk/services/paid-social-media-advertising/",
    "perf":  "/uk/services/performance-marketing-agency/",
    "ecom":  "/services/ecommerce-marketing/",
    "wa":    "/services/whatsapp-marketing/",
    "brand": "/services/branding-and-design/"
  };
  function patch(){
    document.querySelectorAll(".wwd-row").forEach(function(row){
      var dest = MAP[row.getAttribute("data-svc")];
      if (!dest) return;
      row.addEventListener("click", function(e){
        e.stopImmediatePropagation();
        e.preventDefault();
        window.location.href = dest;
      }, true);
    });
    var preview = document.getElementById("wwdPreview");
    if (preview) {
      var fix = function(){
        var active = document.querySelector(".wwd-row.active");
        if (!active) return;
        var dest = MAP[active.getAttribute("data-svc")];
        var cta = preview.querySelector(".pv-cta");
        if (cta && dest) cta.setAttribute("href", dest);
      };
      fix();
      if (window.MutationObserver) {
        new MutationObserver(fix).observe(preview, {childList:true, subtree:true});
      }
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", patch);
  } else {
    patch();
  }
})();
</script>
"""

OVERRIDE_MARKER = "C15 — Force wwd-row clicks"

def main():
    html = PAGE.read_text(encoding="utf-8")
    original = html
    changes = []

    # 1) Mega-menu (each link has role="menuitem" — disambiguates from footer)
    for slug, label in UK_LINK_UPDATES:
        # Reconstruct exact mega-menu anchor (text is escaped & for ampersand)
        label_escaped = label.replace("&", "&amp;")
        old = f'<a href="/{slug}/" role="menuitem">{label_escaped}</a>'
        new = f'<a href="/uk/{slug}/" role="menuitem">{label_escaped}</a>'
        if old in html:
            html = html.replace(old, new, 1)
            changes.append(f"  ✓ mega-menu: /{slug}/ → /uk/{slug}/")
        else:
            changes.append(f"  ⚠ mega-menu: '{old}' not found (text may differ)")

    # 2) Footer Services list — different structure (no role="menuitem")
    for slug, label in FOOTER_LINK_UPDATES:
        label_escaped = label.replace("&", "&amp;")
        old = f'<li><a href="/{slug}/">{label_escaped}</a></li>'
        new = f'<li><a href="/uk/{slug}/">{label_escaped}</a></li>'
        if old in html:
            html = html.replace(old, new, 1)
            changes.append(f"  ✓ footer: /{slug}/ → /uk/{slug}/")
        else:
            changes.append(f"  ⚠ footer: '{old}' not found")

    # 3) Static preview CTA (the "Explore SEO Services" link)
    static_cta_old = '<a class="pv-cta" href="/services/seo/">Explore SEO Services</a>'
    static_cta_new = '<a class="pv-cta" href="/uk/services/seo/">Explore SEO Services</a>'
    if static_cta_old in html:
        html = html.replace(static_cta_old, static_cta_new, 1)
        changes.append("  ✓ static preview CTA href → /uk/seo/")
    else:
        changes.append("  ⚠ static preview CTA not found")

    # 4) Inline override script — only insert if not already there
    if OVERRIDE_MARKER not in html:
        if "</body>" in html:
            html = html.replace("</body>", WWD_OVERRIDE_SCRIPT + "</body>", 1)
            changes.append("  ✓ wwd-override script inserted before </body>")
        else:
            changes.append("  ⚠ no </body> tag found — script not inserted")
    else:
        changes.append("  - wwd-override script already present, skipping")

    # Write out
    if html != original:
        PAGE.write_text(html, encoding="utf-8")
        print("Changes applied:")
        for c in changes: print(c)
    else:
        print("No changes (already in target state).")

if __name__ == "__main__":
    main()
