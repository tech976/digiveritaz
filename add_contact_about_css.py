#!/usr/bin/env python3
"""Style the contact page's "what happens next" prose block.

.c-about is a new class, so it inherits no section padding, and links
inside .prose paragraphs currently compute to the same colour as body
text with no underline -- the 19 internal links were invisible as links.

Also bumps the style.min.css cache-buster. Appending rules without
bumping it is what shipped the broken Ask-AI icons earlier: browsers and
the CDN keep serving the previous stylesheet.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
CSS = SITE / "css"

MARKER = "/* contact: what-happens-next block */"
NEW_VER = "1785900000"

PRETTY = """

/* contact: what-happens-next block */
.c-about{padding:70px 0 90px}
.c-about h2{margin:14px 0 18px}
.c-about h3{margin:34px 0 10px;font-size:1.25rem}
.c-about p{margin:0 0 16px;line-height:1.75}
.c-about p a{
  color:var(--green-dark);font-weight:600;
  text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;
}
.c-about p a:hover{color:var(--green);text-decoration-thickness:2px}
[data-theme="dark"] .c-about p a{color:#22c55e}
@media(max-width:640px){
  .c-about{padding:48px 0 60px}
  .c-about h3{font-size:1.14rem;margin-top:28px}
}
"""

MIN = (
    MARKER
    + ".c-about{padding:70px 0 90px}"
    ".c-about h2{margin:14px 0 18px}"
    ".c-about h3{margin:34px 0 10px;font-size:1.25rem}"
    ".c-about p{margin:0 0 16px;line-height:1.75}"
    ".c-about p a{color:var(--green-dark);font-weight:600;text-decoration:underline;"
    "text-underline-offset:3px;text-decoration-thickness:1px}"
    ".c-about p a:hover{color:var(--green);text-decoration-thickness:2px}"
    '[data-theme="dark"] .c-about p a{color:#22c55e}'
    "@media(max-width:640px){.c-about{padding:48px 0 60px}"
    ".c-about h3{font-size:1.14rem;margin-top:28px}}"
)


def main():
    for name in ("style.css", "style.min.css"):
        p = CSS / name
        src = p.read_text(encoding="utf-8")
        if MARKER in src:
            print(f"  = already has block: {name}")
            continue
        p.write_text(src + (MIN if ".min." in name else PRETTY), encoding="utf-8")
        print(f"  + {name}")

    bumped = 0
    for p in sorted(SITE.rglob("*.html")):
        src = p.read_text(encoding="utf-8")
        new = re.sub(r"(css/style\.min\.css\?v=)\d+", r"\g<1>" + NEW_VER, src)
        if new != src:
            p.write_text(new, encoding="utf-8")
            bumped += 1
    print(f"\ncache-buster bumped to {NEW_VER} in {bumped} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
