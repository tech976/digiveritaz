#!/usr/bin/env python3
"""Sitemap -> seo/data/inventory.json

Walks the sitemap index (local files by default, --live to fetch from
production), classifies each URL into a section, and attaches the focus
keyphrase from keywords.json where one exists. Pages with no keyword cluster
fall back to a keyphrase derived from the slug.

Usage:
  python3 build_inventory.py           # read ../site/sitemap.xml on disk
  python3 build_inventory.py --live    # fetch https://www.digiveritaz.com/sitemap.xml
"""
import json, os, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

SM = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(HERE), "site")
ORIGIN = "https://www.digiveritaz.com"
UA = "Mozilla/5.0 (compatible; DigiVeritazSEOBot/1.0)"


def _local_path(url):
    """Map a production URL back to the file that serves it."""
    path = urllib.parse.urlparse(url).path
    rel = path.strip("/")
    for cand in ([os.path.join(SITE, rel, "sitemap.xml")] if rel.endswith("sitemap.xml") else []):
        if os.path.isfile(cand):
            return cand
    cand = os.path.join(SITE, rel) if rel else os.path.join(SITE, "sitemap.xml")
    return cand if os.path.isfile(cand) else None


def load_xml(url, live):
    if live:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read()
    p = _local_path(url)
    if not p:
        raise FileNotFoundError(url)
    return open(p, "rb").read()


def collect(url, live, seen=None):
    """Returns [(loc, lastmod)] following sitemap indexes one level deep."""
    seen = seen if seen is not None else set()
    if url in seen:
        return []
    seen.add(url)
    root = ET.fromstring(load_xml(url, live))
    tag = root.tag.split("}")[-1]
    out = []
    if tag == "sitemapindex":
        for sm in root.iter(SM + "sitemap"):
            loc = sm.findtext(SM + "loc")
            if loc:
                out += collect(loc.strip(), live, seen)
    else:
        for u in root.iter(SM + "url"):
            loc = u.findtext(SM + "loc")
            if loc:
                out.append((loc.strip(), (u.findtext(SM + "lastmod") or "").strip()))
    return out


def section_of(path):
    p = path.strip("/")
    if not p:                                   return "Home"
    if p.startswith("uk/"):                     return "UK"
    if p.startswith("services/"):               return "Services"
    if p.startswith("blog/"):                   return "Blog"
    if p.startswith("case-study"):              return "Case studies"
    if p.startswith("digital-marketing-agency-in-"): return "Location pages"
    return "Core"


def derive_keyphrase(path):
    """Fallback focus keyphrase for pages with no cluster in the sheet."""
    p = path.strip("/")
    if not p:
        return "digital marketing agency"
    slug = p.split("/")[-1]
    slug = re.sub(r"^(digital-marketing-agency-in-)", "digital marketing agency in ", slug)
    return re.sub(r"[-_]+", " ", slug).strip()


def main():
    live = "--live" in sys.argv
    kw_path = os.path.join(HERE, "data", "keywords.json")
    clusters = {}
    if os.path.isfile(kw_path):
        clusters = json.load(open(kw_path, encoding="utf-8")).get("clusters", {})

    urls = collect(f"{ORIGIN}/sitemap.xml", live)
    seen, pages = set(), []
    for loc, lastmod in urls:
        if loc in seen:
            continue
        seen.add(loc)
        path = urllib.parse.urlparse(loc).path
        cluster = clusters.get(path)
        pages.append({
            "url": loc,
            "path": path,
            "section": section_of(path),
            "lastmod": lastmod or None,
            "keyphrase": cluster["focus"] if cluster else derive_keyphrase(path),
            "keyphrase_source": "sheet" if cluster else "derived",
            "cluster_sheet": cluster["sheet"] if cluster else None,
            "cluster_volume": cluster["total_volume"] if cluster else None,
        })

    pages.sort(key=lambda p: (p["section"] != "Home", p["section"], p["path"]))
    data = {"origin": ORIGIN, "source": "live sitemap" if live else "local sitemap",
            "count": len(pages), "pages": pages}
    out = os.path.join(HERE, "data", "inventory.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    by_sec = {}
    for p in pages:
        by_sec[p["section"]] = by_sec.get(p["section"], 0) + 1
    print(f"{len(pages)} URLs -> {out}")
    for s, n in sorted(by_sec.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {s}")
    print(f"  {sum(1 for p in pages if p['keyphrase_source'] == 'sheet')} pages have a keyphrase from the sheet")


if __name__ == "__main__":
    main()
