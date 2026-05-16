#!/usr/bin/env python3
"""Remove the middle phone number (+91 70214 50830) site-wide.

Per HR: footer contact section should list only:
  +91 99566 55662
  +91 70453 37060

The third number (+91 70214 50830) was historically present in 3
contexts (footer phone column, contact page sidebar, thank-you message)
— removing all three.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

REPLACEMENTS = [
    # Footer phone column — "<br><a href='...70214...'>+91 70214 50830</a>"
    ('<br><a href="tel:+917021450830">+91 70214 50830</a>', ''),
    # Contact-us sidebar — "+91 70214 50830 &middot; +91 70453 37060"
    ('<a href="tel:+917021450830">+91 70214 50830</a> &middot; ', ''),
    # Thank-you message — "..., +91 70214 50830 or +91 70453 37060"
    (', <a href="tel:+917021450830">+91 70214 50830</a>', ''),
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
