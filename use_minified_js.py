#!/usr/bin/env python3
"""Point the site at the newly minified JS bundles.

Three scripts were still served unminified:
  ai-news.js   11.0 KB -> 5.7 KB   (loaded by /ai-news/)
  dv-lead.js   31.2 KB -> 21.7 KB  (loaded by /get-proposal/)
  blog-cta.js  24.5 KB -> 14.7 KB  (injected by main.js on blog pages)

blog-cta.js is not referenced from any HTML -- main.js/main.min.js append
it at runtime -- so its <script src> lives inside those two bundles and is
rewritten here too. Because main.min.js itself changes as a result, its
?v= must be bumped on every page or browsers keep the cached copy that
still points at the unminified file.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

NEW_VER = "1786000000"

# (file glob or explicit path, old basename, new basename)
SWAPS = [
    ("ai-news.html", "ai-news.js", "ai-news.min.js"),
    ("get-proposal/index.html", "dv-lead.js", "dv-lead.min.js"),
    ("js/main.js", "blog-cta.js", "blog-cta.min.js"),
    ("js/main.min.js", "blog-cta.js", "blog-cta.min.js"),
    # main.js injects the site-wide lead popup on every page too
    ("js/main.js", "dv-lead.js", "dv-lead.min.js"),
    ("js/main.min.js", "dv-lead.js", "dv-lead.min.js"),
]


def main():
    for rel, old, new in SWAPS:
        p = SITE / rel
        src = p.read_text(encoding="utf-8")
        # only rewrite the /js/<name>?v=<n> reference, never other mentions
        pat = re.compile(r"/js/" + re.escape(old) + r"\?v=\d+")
        n = len(pat.findall(src))
        if not n:
            print(f"  ! no reference to {old} in {rel}")
            continue
        p.write_text(pat.sub(f"/js/{new}?v={NEW_VER}", src), encoding="utf-8")
        print(f"  + {rel}: {old} -> {new}  ({n} ref)")

    # main.min.js changed, so every page must refetch it
    bumped = 0
    for p in sorted(SITE.rglob("*.html")):
        src = p.read_text(encoding="utf-8")
        new = re.sub(r"(/js/main\.min\.js\?v=)\d+", r"\g<1>" + NEW_VER, src)
        if new != src:
            p.write_text(new, encoding="utf-8")
            bumped += 1
    print(f"\nmain.min.js cache-buster bumped to {NEW_VER} in {bumped} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
