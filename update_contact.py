#!/usr/bin/env python3
"""Contact-info sweep across the static site.

Per HR (16/05/2026): the public/footer contacts are now
  durvamukherjee@digiveritaz.com  (replaces info@)
  daniel@digiveritaz.com          (replaces mihir@)
and the address line should read "Mumbai, Maharashtra 400088" instead
of just "Mumbai 400088". The Privacy Officer reference in the privacy
policy is also updated.

Touches every .html in site/ plus build.py so the next rebuild won't
regress to the old values.
"""
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"
TARGETS = sorted(SITE.glob("*.html")) + [SITE / "build.py"]

# Order matters: handle "Privacy Officer: Mihir Lunia · mihir@..." before
# the bulk mihir@ -> daniel@ sweep so the name stays in sync with the email.
REPLACEMENTS = [
    ("Mihir Lunia · mihir@digiveritaz.com",
     "Durva Mukherjee · durvamukherjee@digiveritaz.com"),
    ("emailing mihir@digiveritaz.com",
     "emailing durvamukherjee@digiveritaz.com"),
    ("info@digiveritaz.com",
     "durvamukherjee@digiveritaz.com"),
    ("mihir@digiveritaz.com",
     "daniel@digiveritaz.com"),
    ("Mumbai 400088",
     "Mumbai, Maharashtra 400088"),
]


def main() -> int:
    if not SITE.is_dir():
        print(f"ERROR: site dir not found at {SITE}")
        return 1

    changed = 0
    for p in TARGETS:
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
