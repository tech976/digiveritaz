#!/usr/bin/env python3
"""One-shot sweep to refresh the footer tagline across the site.

Old: "Mumbai-based digital marketing agency helping brands across India
      achieve measurable ROI through SEO, paid media, and performance
      marketing."

New: "DigiVeritaz is a Mumbai-based digital marketing agency helping
      brands across India achieve measurable ROI through SEO, Paid Media,
      Performance Marketing <strong>and MORE</strong>."

Also switches data-i18n="foot.tag" -> "foot.tag.html" so the runtime
i18n applier renders the <strong> instead of escaping it.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

OLD_TEXT = "Mumbai-based digital marketing agency helping brands across India achieve measurable ROI through SEO, paid media, and performance marketing."
NEW_HTML = "DigiVeritaz is a Mumbai-based digital marketing agency helping brands across India achieve measurable ROI through SEO, Paid Media, Performance Marketing <strong>and MORE</strong>."

REPLACEMENTS = [
    (OLD_TEXT, NEW_HTML),
    ('data-i18n="foot.tag"', 'data-i18n="foot.tag.html"'),
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
