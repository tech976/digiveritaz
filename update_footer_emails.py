#!/usr/bin/env python3
"""Reorder footer emails site-wide to: info@ -> daniel@ -> durvamukherjee@.

User asked to add info@digiveritaz.com back as the primary contact, with
daniel@ second and durvamukherjee@ third in the footer "Email" row of
every page.

Handles two presentation patterns:
1. Footer column (and FAQ/privacy contact strip): three emails joined by
   <br>, e.g.
       <a ...>durvamukherjee...</a><br><a ...>daniel...</a>
2. Contact page sidebar (build.py only): primary email link + sub line.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

# Pattern 1: footer column / contact strip — replace the 2-email block
# with a 3-email block in the requested order.
OLD_FOOTER_EMAILS = (
    '<a href="mailto:durvamukherjee@digiveritaz.com">durvamukherjee@digiveritaz.com</a>'
    '<br><a href="mailto:daniel@digiveritaz.com">daniel@digiveritaz.com</a>'
)
NEW_FOOTER_EMAILS = (
    '<a href="mailto:info@digiveritaz.com">info@digiveritaz.com</a>'
    '<br><a href="mailto:daniel@digiveritaz.com">daniel@digiveritaz.com</a>'
    '<br><a href="mailto:durvamukherjee@digiveritaz.com">durvamukherjee@digiveritaz.com</a>'
)

# Pattern 2: contact-page sidebar — primary email + .sv-sub.
# Currently:   <a class="sv" href="mailto:durva...">durva...</a>
#              <span class="sv-sub"><a href="mailto:daniel...">daniel...</a></span>
# Wanted:      <a class="sv" href="mailto:info...">info...</a>
#              <span class="sv-sub">
#                <a href="mailto:daniel...">daniel...</a> &middot;
#                <a href="mailto:durva...">durva...</a>
#              </span>
OLD_SIDEBAR_PRIMARY = (
    '<a class="sv" href="mailto:durvamukherjee@digiveritaz.com">'
    'durvamukherjee@digiveritaz.com</a>'
)
NEW_SIDEBAR_PRIMARY = (
    '<a class="sv" href="mailto:info@digiveritaz.com">'
    'info@digiveritaz.com</a>'
)
OLD_SIDEBAR_SUB = (
    '<span class="sv-sub">'
    '<a href="mailto:daniel@digiveritaz.com">daniel@digiveritaz.com</a>'
    '</span>'
)
NEW_SIDEBAR_SUB = (
    '<span class="sv-sub">'
    '<a href="mailto:daniel@digiveritaz.com">daniel@digiveritaz.com</a>'
    ' &middot; '
    '<a href="mailto:durvamukherjee@digiveritaz.com">durvamukherjee@digiveritaz.com</a>'
    '</span>'
)

REPLACEMENTS = [
    (OLD_FOOTER_EMAILS, NEW_FOOTER_EMAILS),
    (OLD_SIDEBAR_PRIMARY, NEW_SIDEBAR_PRIMARY),
    (OLD_SIDEBAR_SUB, NEW_SIDEBAR_SUB),
]


def main() -> int:
    if not SITE.is_dir():
        print(f"ERROR: site dir not found at {SITE}")
        return 1
    targets = sorted(SITE.glob("*.html")) + [SITE / "build.py"]
    changed = 0
    for p in targets:
        if not p.is_file():
            continue
        src = p.read_text(encoding="utf-8")
        new = src
        for old, repl in REPLACEMENTS:
            new = new.replace(old, repl)
        if new != src:
            p.write_text(new, encoding="utf-8")
            changed += 1
            print(f"  ✓ {p.name}")
    print(f"\nTotal files updated: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
