#!/usr/bin/env python3
"""
DigiVeritaz chatbot — knowledge-base ingestion.

Crawls the site's own service pages, case studies and FAQ, strips the
boilerplate (nav/header/footer/scripts), chunks the readable text, and writes
a single committed file: site/api/kb_index.json

This is intentionally dependency-free (stdlib only) and needs NO API key.
Retrieval at runtime is lexical (TF-IDF style) over these chunks — small site,
fast, no vector DB, no embeddings cost. (The schema leaves room to add an
"embedding" field later if you want to upgrade to vector search.)

Usage:
    python chatbot/ingest.py
"""
import os, re, json, html
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT  = os.path.join(SITE, "api", "kb_index.json")

# Pages NOT worth putting in the KB
SKIP_TOPLEVEL = {
    "privacy-policy.html", "terms-and-conditions.html", "thank-you.html",
    "404.html", "sitemap.html",
}
SKIP_TAGS = {"script", "style", "svg", "noscript", "header", "footer", "nav", "button", "form"}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip_depth = 0
        self.parts = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag in SKIP_TAGS:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.skip_depth == 0:
            t = data.strip()
            if t:
                self.parts.append(t)


def file_to_url(path):
    rel = os.path.relpath(path, SITE).replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    rel = rel[:-len(".html")] if rel.endswith(".html") else rel
    if rel.endswith("/index"):
        rel = rel[:-len("/index")]
    return "/" + rel + "/"


def clean_title(t):
    t = re.sub(r"\s+", " ", html.unescape(t)).strip()
    # drop trailing "| DigiVeritaz ..." style suffixes
    t = re.split(r"\s*[|–—-]\s*DigiVeritaz", t)[0].strip()
    return t or "DigiVeritaz"


def chunk_text(text, target=750, hard=1000):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, cur = [], ""
    for s in sentences:
        if not s:
            continue
        if len(cur) + len(s) + 1 <= target or not cur:
            cur = (cur + " " + s).strip()
            if len(cur) >= hard:
                chunks.append(cur); cur = ""
        else:
            chunks.append(cur); cur = s
    if cur.strip():
        chunks.append(cur.strip())
    return [c for c in chunks if len(c) > 60]


def extract(path):
    raw = open(path, encoding="utf-8").read()
    p = TextExtractor()
    try:
        p.feed(raw)
    except Exception:
        pass
    text = re.sub(r"\s+", " ", html.unescape(" ".join(p.parts))).strip()
    return clean_title(p.title), text


def gather_files():
    files = []
    for name in sorted(os.listdir(SITE)):
        if name.endswith(".html") and name not in SKIP_TOPLEVEL:
            files.append(os.path.join(SITE, name))
    cs = os.path.join(SITE, "case-study")
    if os.path.isdir(cs):
        for name in sorted(os.listdir(cs)):
            if name.endswith(".html"):
                files.append(os.path.join(cs, name))
    return files


def main():
    chunks = []
    pages = 0
    for path in gather_files():
        title, text = extract(path)
        if len(text) < 120:
            continue
        url = file_to_url(path)
        pages += 1
        for i, c in enumerate(chunk_text(text)):
            chunks.append({"id": f"{url}#{i}", "url": url, "title": title, "text": c})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"pages": pages, "count": len(chunks), "chunks": chunks},
                  f, ensure_ascii=False)
    print(f"Ingested {pages} pages -> {len(chunks)} chunks")
    print("Wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
