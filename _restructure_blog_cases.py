#!/usr/bin/env python3
"""Physically move blog & case-study HTML files into subdirectories so
Vercel's native cleanUrls serves /blog/foo/ -> blog/foo.html without
any rewrite gymnastics.

  site/blog-foo.html          -> site/blog/foo.html
  site/blog.html              -> site/blog/index.html
  site/case-study-foo.html    -> site/case-study/foo.html
  site/case-study.html        -> site/case-study/index.html

Asset paths in the HTML are already absolute (/css/..., /assets/...),
so moving the files to a subdir won't break anything.
"""
import pathlib, shutil

SITE = pathlib.Path(__file__).resolve().parent / "site"
moved = []

def move(src: pathlib.Path, dst: pathlib.Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    moved.append((src.name, str(dst.relative_to(SITE))))
    print(f"  {src.name}  ->  {dst.relative_to(SITE)}")

# Listing pages → directory index
for listing in ("blog", "case-study"):
    src = SITE / f"{listing}.html"
    dst = SITE / listing / "index.html"
    if src.exists():
        move(src, dst)

# Individual posts/cases → strip prefix into the subdir
for kind in ("blog", "case-study"):
    prefix = f"{kind}-"
    for src in sorted(SITE.glob(f"{prefix}*.html")):
        slug = src.stem[len(prefix):]   # 'blog-foo' -> 'foo'
        dst = SITE / kind / f"{slug}.html"
        move(src, dst)

print(f"\nTotal moved: {len(moved)}")
print("\nVerify new tree:")
import subprocess
for d in ("blog", "case-study"):
    p = SITE / d
    if p.is_dir():
        files = sorted(p.iterdir())
        print(f"  {d}/  ({len(files)} files)")
        for f in files[:3]:
            print(f"    {f.name}")
        if len(files) > 3:
            print(f"    ... +{len(files) - 3} more")
