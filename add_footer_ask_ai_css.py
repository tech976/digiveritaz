#!/usr/bin/env python3
"""Append the .foot-askai styles to every CSS bundle a page might load.

204 pages load style.min.css; index.html loads home-bundle.min.css plus
home-dark.min.css when the dark theme is active. The tiles stay white in
both themes so the full-colour AI logos remain legible against the light
footer gradient and the dark footer alike.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSS = ROOT / "site" / "css"

MARKER = "/* ask-ai footer row */"

PRETTY = """

/* ask-ai footer row */
.foot-askai{margin:0 0 26px}
/* outrank .site-footer h4, which uppercases and letter-spaces every footer heading */
.site-footer .foot-askai-title{
  font-size:1.06rem;font-weight:700;letter-spacing:-.01em;
  text-transform:none;margin:0 0 14px;color:#0f172a;
}
.foot-askai-row{display:flex;flex-wrap:wrap;gap:12px}
.askai-btn{
  width:52px;height:52px;border-radius:14px;
  border:1px solid #e2e8f0;background:#fff;
  display:grid;place-items:center;transition:.25s ease;
  box-shadow:0 4px 12px rgba(17,24,39,.04);
}
.askai-btn:hover{
  border-color:rgba(34,197,94,.5);transform:translateY(-3px);
  box-shadow:0 10px 24px rgba(34,197,94,.18);
}
.askai-btn svg{width:26px;height:26px;display:block}
[data-theme="dark"] .site-footer .foot-askai-title{color:#fff}
[data-theme="dark"] .askai-btn{background:#fff;border-color:rgba(255,255,255,.16);box-shadow:none}
[data-theme="dark"] .askai-btn:hover{border-color:rgba(34,197,94,.6);box-shadow:0 10px 24px rgba(34,197,94,.25)}
/* tile size stays 52px on mobile to line up with .foot-socials above */
@media(max-width:520px){
  .site-footer .foot-askai-title{font-size:1rem;margin-bottom:12px}
  .foot-askai-row{gap:10px}
}
"""

MIN = (
    MARKER
    + '.foot-askai{margin:0 0 26px}'
    '.site-footer .foot-askai-title{font-size:1.06rem;font-weight:700;letter-spacing:-.01em;'
    'text-transform:none;margin:0 0 14px;color:#0f172a}'
    '.foot-askai-row{display:flex;flex-wrap:wrap;gap:12px}'
    '.askai-btn{width:52px;height:52px;border-radius:14px;border:1px solid #e2e8f0;background:#fff;'
    'display:grid;place-items:center;transition:.25s ease;box-shadow:0 4px 12px rgba(17,24,39,.04)}'
    '.askai-btn:hover{border-color:rgba(34,197,94,.5);transform:translateY(-3px);'
    'box-shadow:0 10px 24px rgba(34,197,94,.18)}'
    '.askai-btn svg{width:26px;height:26px;display:block}'
    '[data-theme="dark"] .site-footer .foot-askai-title{color:#fff}'
    '[data-theme="dark"] .askai-btn{background:#fff;border-color:rgba(255,255,255,.16);box-shadow:none}'
    '[data-theme="dark"] .askai-btn:hover{border-color:rgba(34,197,94,.6);box-shadow:0 10px 24px rgba(34,197,94,.25)}'
    '@media(max-width:520px){.site-footer .foot-askai-title{font-size:1rem;margin-bottom:12px}'
    '.foot-askai-row{gap:10px}}'
)

TARGETS = [
    "style.css",
    "style.min.css",
    "home.css",
    "home.min.css",
    "home-bundle.min.css",
    "home-dark.min.css",
]


def main() -> int:
    changed = 0
    for name in TARGETS:
        p = CSS / name
        if not p.is_file():
            print(f"  - skip (missing): {name}")
            continue
        src = p.read_text(encoding="utf-8")
        if MARKER in src:
            print(f"  = already has block: {name}")
            continue
        p.write_text(src + (MIN if ".min." in name else PRETTY), encoding="utf-8")
        print(f"  + {name}")
        changed += 1
    print(f"\nCSS files updated: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
