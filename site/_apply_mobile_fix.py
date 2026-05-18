#!/usr/bin/env python3
"""Replace the inline mobile-fix <style> block with a *minimal* version that
ONLY contains the mega-menu finger-slip guard. The previous version added
over-aggressive header/hero pointer-events rules with !important that
appeared to break click handling inside the mobile hamburger drawer on
some pages. The global css/style.css already carries the header + hero
rules, so duplicating them inline was redundant and harmful.

Idempotent. Run once from site/:
    python3 _apply_mobile_fix.py
"""
import pathlib, re

SITE = pathlib.Path(__file__).parent
NEW_CSS_VER = "1779094200"
START_TAG = "<style>"
END_TAG = "</style>"
OUR_MARKER = "Mobile mega-menu finger-slip fix"

NEW_BLOCK = """<style>
/* Mobile mega-menu safety guard — keeps the 41-service dropdown on
   desktop unchanged. On mobile/tablet (<=1050px):
     1. While the hamburger drawer is closed (.nav ul has no .open class),
        the entire mega-menu subtree is display:none + visibility:hidden +
        pointer-events:none so none of its 41 links can be touched.
     2. The :focus-within auto-open trigger is suppressed so a stray
        focus cannot reveal the dropdown — only the JS-driven .open class
        controlled by tapping "Services" can.
   Once the drawer is open AND Services has been tapped, every one of
   the 41 service links is fully tappable as expected. */
@media (max-width:1050px){
  .has-mega:focus-within .dd-menu.mega-menu:not(.force-open){
    display:none !important;
  }
  .nav ul:not(.open) .dd-menu.mega-menu,
  .nav ul:not(.open) .dd-menu.mega-menu *{
    display:none !important;
    visibility:hidden !important;
    pointer-events:none !important;
  }
}
</style>"""

# Matches our previously-injected <style>...</style> block — anchored by
# either of the two markers we have used. Greedy across newlines.
EXISTING_BLOCK_RE = re.compile(
    r"<style>\s*/\* (?:Hard inline override|Mobile hardening|Mobile mega-menu finger-slip fix|Mobile mega-menu safety guard).*?</style>",
    re.DOTALL,
)
CSS_LINK_RE = re.compile(r'(<link rel="stylesheet" href="css/style\.css\?v=)\d+(">)')

patched, replaced, fresh, unchanged = [], [], [], []

for html in sorted(SITE.glob("*.html")):
    text = html.read_text()
    original = text

    # Bump css cache version
    text = CSS_LINK_RE.sub(
        lambda m: f"{m.group(1)}{NEW_CSS_VER}{m.group(2)}", text, count=1
    )

    if EXISTING_BLOCK_RE.search(text):
        text = EXISTING_BLOCK_RE.sub(NEW_BLOCK, text, count=1)
        replaced.append(html.name)
    else:
        text = CSS_LINK_RE.sub(
            lambda m: f"{m.group(1)}{NEW_CSS_VER}{m.group(2)}\n" + NEW_BLOCK,
            text,
            count=1,
        )
        fresh.append(html.name)

    if text != original:
        html.write_text(text)
        patched.append(html.name)
    else:
        unchanged.append(html.name)

print(f"Patched {len(patched)} files ({len(replaced)} replaced, {len(fresh)} fresh).")
if unchanged:
    print(f"Unchanged: {len(unchanged)}")
    for n in unchanged:
        print(f"  - {n}")
