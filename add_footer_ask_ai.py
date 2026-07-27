#!/usr/bin/env python3
"""One-shot sweep to add the "Ask AI about DigiVeritaz" block to the footer.

Adds a row of deep-links into the major AI assistants (ChatGPT, Gemini,
Perplexity, Claude), each pre-loaded with a research prompt about
DigiVeritaz. This is a GEO/AEO play: it pushes real users into asking
assistants about us, which in turn feeds those assistants' retrieval.

The block is injected directly after the closing </div> of .foot-socials
inside the brand column, so it inherits the existing footer grid.

Touches every built page under site/ (root, blog/, case-study/, uk/) plus
the FOOT template in site/build.py so future builds keep it.
"""
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

PROMPT = (
    "what makes DigiVeritaz a capable and trustworthy digital marketing agency "
    "in india. Research DigiVeritaz public website and public-facing information. "
    "Cover: Digital Marketing, SEO, Performance Marketing, Paid Media, Social Media "
    "Marketing, Ecommerce Marketing, Website Design & Development, Analytics, "
    "Creative Services, Growth Strategy, Client portfolio. Output: 1. A 150-200 word "
    'summary 2. 5 short bullet points "Why DigiVeritaz is best for digital services" '
    "3. Final Verdict"
)
Q = quote(PROMPT, safe="")

# Gemini has no supported prefill on gemini.google.com, so we send users to
# Google's AI Mode (udm=50), which does accept ?q= and answers with Gemini.
ENGINES = [
    ("ChatGPT", f"https://chatgpt.com/?hints=search&q={Q}"),
    ("Google Gemini", f"https://www.google.com/search?udm=50&q={Q}"),
    ("Perplexity", f"https://www.perplexity.ai/search/new?q={Q}"),
    ("Claude", f"https://claude.ai/new?q={Q}"),
]

ICONS = {
    "ChatGPT": (
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#000" d="M22.28 9.82a5.99 5.99 0 0 0-.52-4.91 6.05 6.05 0 0 0-6.51-2.9A6 6 0 0 0 4.98 4.18a5.99 5.99 0 0 0-4 2.9 6.05 6.05 0 0 0 .74 7.1 5.98 5.98 0 0 0 .51 4.91 6.05 6.05 0 0 0 6.52 2.9A5.98 5.98 0 0 0 13.26 24a6.06 6.06 0 0 0 5.77-4.21 5.99 5.99 0 0 0 3.99-2.9 6.06 6.06 0 0 0-.74-7.07Zm-9.02 12.6a4.48 4.48 0 0 1-2.88-1.04l.14-.08 4.78-2.76a.79.79 0 0 0 .39-.68v-6.74l2.02 1.17a.07.07 0 0 1 .04.05v5.58a4.5 4.5 0 0 1-4.49 4.5ZM3.6 18.3a4.47 4.47 0 0 1-.54-3.01l.14.09 4.79 2.76a.78.78 0 0 0 .78 0l5.84-3.37v2.33a.08.08 0 0 1-.03.06L9.74 19.9a4.5 4.5 0 0 1-6.14-1.64ZM2.34 7.9a4.48 4.48 0 0 1 2.35-1.97v5.68a.77.77 0 0 0 .38.67l5.82 3.36-2.02 1.17a.08.08 0 0 1-.07 0l-4.84-2.8A4.5 4.5 0 0 1 2.34 7.9Zm16.6 3.86-5.84-3.38 2.02-1.16a.08.08 0 0 1 .07 0l4.84 2.8a4.49 4.49 0 0 1-.68 8.1v-5.69a.79.79 0 0 0-.4-.67Zm2.01-3.02-.14-.09-4.78-2.79a.78.78 0 0 0-.79 0L9.4 9.23V6.9a.07.07 0 0 1 .03-.06l4.84-2.79a4.5 4.5 0 0 1 6.68 4.66ZM8.3 12.87l-2.02-1.17a.08.08 0 0 1-.04-.06V6.07a4.5 4.5 0 0 1 7.38-3.45l-.14.08L8.7 5.46a.79.79 0 0 0-.39.68l-.01 6.73Zm1.1-2.36L12 9.01l2.6 1.5v3l-2.6 1.5-2.6-1.5v-3Z"/></svg>'
    ),
    "Google Gemini": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<defs><linearGradient id="dvGemGrad" x1="0" y1="1" x2="1" y2="0">'
        '<stop offset="0" stop-color="#1C7DFF"/><stop offset=".52" stop-color="#1C69FF"/>'
        '<stop offset="1" stop-color="#F0DCD6"/></linearGradient></defs>'
        '<path fill="url(#dvGemGrad)" d="M12 24A14.3 14.3 0 0 0 0 12 14.3 14.3 0 0 0 12 0a14.3 14.3 0 0 0 12 12 14.3 14.3 0 0 0-12 12Z"/></svg>'
    ),
    "Perplexity": (
        '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#20808D" '
        'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2.6v6.5M12 14.9v6.5"/>'
        '<path d="M12 9.1 4.4 3.1v6M12 9.1l7.6-6v6"/>'
        '<path d="M12 14.9 4.4 20.9v-6M12 14.9l7.6 6v-6"/>'
        '<rect x="2.6" y="9.1" width="18.8" height="5.8" rx=".4"/></svg>'
    ),
    "Claude": (
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#D97757" d="m4.71 15.14 4.68-2.63.08-.23-.08-.13h-.23l-.79-.05-2.7-.07-2.34-.1-2.27-.12-.57-.12L0 10.94l.05-.35.48-.32.68.06 1.51.1 2.26.16 1.64.1 2.43.25h.39l.05-.16-.13-.1-.1-.09-2.35-1.59-2.54-1.68-1.33-.97-.72-.49-.36-.46-.16-1L2.45 4l.87.06.22.06.88.68 1.89 1.46 2.46 1.82.36.3.15-.1.02-.08-.16-.27L9.1 5.3 7.71 2.9l-.62-.99-.16-.6A2.9 2.9 0 0 1 6.83.6L7.57.1 8 .4l.42.32.62 1.41 1 2.24 1.56 3.04.46.9.24.84.09.26h.16V9.3l.13-1.72.24-2.11.23-2.72.08-.76.38-.92.75-.5.59.29.48.69-.07.44-.29 1.9-.57 2.98-.37 2h.22l.25-.25 1.01-1.35 1.7-2.12.75-.85.88-.93.56-.45h1.07l.78 1.17-.35 1.2-1.1 1.4-.92 1.18-1.31 1.77-.82 1.42.08.11.2-.02 3.06-.65 1.65-.3 1.97-.34.89.42.1.42-.35.86-2.1.52-2.46.49-3.67.87-.04.03.05.06 1.66.16.7.04h1.73l3.22.24.84.55.5.68-.08.51-1.29.66-1.75-.42-4.08-.97-1.4-.35h-.19v.12l1.16 1.14 2.13 1.93 2.67 2.48.14.62-.35.49-.36-.05-2.36-1.77-.91-.8-2.06-1.73h-.14v.18l.48.69 2.5 3.77.13 1.15-.18.38-.65.23-.71-.13-1.47-2.06-1.51-2.32-1.22-2.07-.15.08-.72 7.7-.33.4-.78.3-.64-.5-.35-.78.35-1.58.4-2.05.34-1.64.3-2.02.18-.67-.01-.05-.15.02-1.52 2.08-2.3 3.11-1.83 1.96-.44.17-.76-.4.07-.7.42-.63 2.53-3.22 1.53-2 .98-1.15-.01-.16h-.06L4.9 18.4l-2.4 1.55-.4.05-.68-.65.08-.42.33-.34 2.7-1.86-.01.01Z"/></svg>'
    ),
}

HEADING = "Ask AI about DigiVeritaz"


def build_block(indent: str) -> str:
    lines = [
        f'{indent}<div class="foot-askai">',
        f'{indent}  <h4 class="foot-askai-title">{HEADING}</h4>',
        f'{indent}  <div class="foot-askai-row">',
    ]
    for name, url in ENGINES:
        lines.append(
            f'{indent}    <a class="askai-btn" href="{url.replace("&", "&amp;")}" '
            f'target="_blank" rel="noopener nofollow" '
            f'aria-label="Ask {name} about DigiVeritaz" title="Ask {name} about DigiVeritaz">'
            f'{ICONS[name]}</a>'
        )
    lines += [f'{indent}  </div>', f'{indent}</div>']
    return "\n".join(lines)


ANCHOR = '<div class="foot-socials">'


def patch(src):
    """Insert the block right after the .foot-socials container closes."""
    if 'class="foot-askai"' in src:  # already done
        return None
    start = src.find(ANCHOR)
    if start == -1:
        return None

    # Walk forward balancing <div>/</div> to find this container's close tag.
    depth = 0
    i = start
    while i < len(src):
        if src.startswith("<div", i):
            depth += 1
            i += 4
        elif src.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                break
        else:
            i += 1
    if depth != 0:
        return None

    line_start = src.rfind("\n", 0, start) + 1
    indent = src[line_start:start]
    if indent.strip():
        indent = "          "

    return src[:i] + "\n\n" + build_block(indent) + src[i:]


def main() -> int:
    if not SITE.is_dir():
        print(f"ERROR: site dir not found at {SITE}")
        return 1

    targets = sorted(SITE.rglob("*.html")) + [SITE / "build.py"]
    changed, skipped = 0, 0
    for p in targets:
        if not p.is_file():
            continue
        src = p.read_text(encoding="utf-8")
        new = patch(src)
        if new is None:
            if ANCHOR in src:
                skipped += 1
            continue
        p.write_text(new, encoding="utf-8")
        changed += 1

    print(f"Updated: {changed}   already-had-block/unparsed: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
