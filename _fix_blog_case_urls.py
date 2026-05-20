#!/usr/bin/env python3
"""Convert flat /blog-foo/ and /case-study-foo/ URLs to nested
/blog/foo/ and /case-study/foo/ across all HTML + build.py + sitemap.

Touches:
  href="/blog-foo/"                  -> href="/blog/foo/"
  href="/blog-foo/#anchor"           -> href="/blog/foo/#anchor"
  href="/case-study-foo/"            -> href="/case-study/foo/"
  <loc>.../blog-foo.html</loc>       -> <loc>.../blog/foo/</loc>   (sitemap)
"""
import pathlib, re

SITE = pathlib.Path(__file__).resolve().parent / "site"

# href="/blog-<slug>/[#frag]"  or  href="/blog-<slug>/"
BLOG_HREF = re.compile(r'href="/blog-([^"/]+)/(#[^"]*)?"')
CASE_HREF = re.compile(r'href="/case-study-([^"/]+)/(#[^"]*)?"')

# Sitemap <loc> entries — original format ends in .html (no trailing slash)
# but also catch any with trailing slash for safety.
SITEMAP_BLOG = re.compile(r'<loc>https://digiveritaz\.com/blog-([^<]+?)</loc>')
SITEMAP_CASE = re.compile(r'<loc>https://digiveritaz\.com/case-study-([^<]+?)</loc>')

def _href_fix(prefix: str):
    def repl(m):
        slug = m.group(1)
        frag = m.group(2) or ""
        return f'href="/{prefix}/{slug}/{frag}"'
    return repl

def _sitemap_fix(prefix: str):
    def repl(m):
        slug = m.group(1).strip("/")
        if slug.endswith(".html"):
            slug = slug[:-5]
        return f'<loc>https://digiveritaz.com/{prefix}/{slug}/</loc>'
    return repl

targets = list(SITE.glob("*.html")) + [SITE / "build.py", SITE / "sitemap.xml"]
totals = {"blog_href": 0, "case_href": 0, "blog_loc": 0, "case_loc": 0}
for p in targets:
    if not p.is_file():
        continue
    text = p.read_text(encoding="utf-8")
    new = text
    new, n1 = BLOG_HREF.subn(_href_fix("blog"), new)
    new, n2 = CASE_HREF.subn(_href_fix("case-study"), new)
    n3 = n4 = 0
    if p.suffix == ".xml":
        new, n3 = SITEMAP_BLOG.subn(_sitemap_fix("blog"), new)
        new, n4 = SITEMAP_CASE.subn(_sitemap_fix("case-study"), new)
    if new != text:
        p.write_text(new, encoding="utf-8")
        totals["blog_href"] += n1
        totals["case_href"] += n2
        totals["blog_loc"]  += n3
        totals["case_loc"]  += n4
        print(f"  ✓ {p.name}: blog-href={n1} case-href={n2} blog-loc={n3} case-loc={n4}")

print()
for k, v in totals.items():
    print(f"  {k:12s} = {v}")
