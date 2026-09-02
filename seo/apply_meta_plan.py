#!/usr/bin/env python3
"""Apply data/meta_plan.json to the site.

Writes each page's title and description to all three places that matter, so a
later `python3 build.py` cannot revert them:

  1. site/**.html            the 6 meta fields actually served
  2. site/services_data.py   source of truth for the 41 service pages
  3. site/build.py           source of truth for core pages written by write()

Dry run by default -- nothing is written without --write.

Usage:
  python3 apply_meta_plan.py                 # show what would change
  python3 apply_meta_plan.py --write         # apply the sheet verbatim
  python3 apply_meta_plan.py --write --trimmed   # apply without the stock endings
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(HERE), "site")

# services_data.py still carries the pre-migration slugs for these two.
SLUG_FIX = {"whatsapp-marketing.html": "whatsapp-marketing-services.html",
            "organic-marketing.html": "organic-marketing-services.html"}
# build.py addresses case-study by its pre-migration filename.
BUILD_NAME = {"case-study/index.html": "case-study.html"}


def esc(t):
    """The site writes & as &amp; throughout; nothing else is escaped."""
    return t.replace("&", "&amp;")


def resolve(path):
    rel = path.strip("/")
    if not rel:
        return os.path.join(SITE, "index.html")
    for c in (os.path.join(SITE, rel + ".html"), os.path.join(SITE, rel, "index.html")):
        if os.path.isfile(c):
            return c
    return None


def update_html(fp, title, desc, write):
    t, d = esc(title), esc(desc)
    src = open(fp, encoding="utf-8").read()
    out, total = src, 0
    for pat, repl in [
        (r"<title>[^<]*</title>", f"<title>{t}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{d}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{d}">'),
        (r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{t}">'),
        (r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{d}">'),
    ]:
        out, n = re.subn(pat, lambda _m, r=repl: r, out, count=1)
        total += n
    if total != 6:
        raise RuntimeError(f"{os.path.relpath(fp, SITE)}: expected 6 meta fields, found {total}")
    changed = out != src
    if write and changed:
        open(fp, "w", encoding="utf-8").write(out)
    return changed


def py_lit(s):
    """Render as a single-quoted Python literal, matching the file's style."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def update_services_data(by_slug, write):
    fp = os.path.join(SITE, "services_data.py")
    lines = open(fp, encoding="utf-8").read().splitlines(keepends=True)
    marks = [(i, m.group(1)) for i, l in enumerate(lines)
             if (m := re.match(r"\s*'site_slug':\s*'([^']+)'", l))]
    marks.append((len(lines), ""))

    done, hit = 0, set()
    for (start, slug), (end, _) in zip(marks, marks[1:]):
        e = by_slug.get(slug)
        if not e:
            continue
        hit.add(slug)
        touched = False
        for i in range(start, end):
            m = re.match(r"(\s*)'(meta_title|meta_desc)':\s*", lines[i])
            if not m:
                continue
            val = e["title"] if m.group(2) == "meta_title" else e["desc"]
            new = f"{m.group(1)}'{m.group(2)}': {py_lit(val)},\n"
            if lines[i] != new:
                lines[i] = new
                touched = True
        done += touched
    if write and done:
        open(fp, "w", encoding="utf-8").write("".join(lines))
    return done, set(by_slug) - hit


def update_build_py(by_name, write):
    fp = os.path.join(SITE, "build.py")
    src = open(fp, encoding="utf-8").read()
    out, done, missing = src, 0, []
    for name, e in by_name.items():
        # write("name.html",\n "Title",\n "Desc",  -- title/desc are the next
        # two string literals after the filename.
        pat = re.compile(
            r'(write\(\s*"' + re.escape(name) + r'"\s*,\s*)'
            r'("(?:[^"\\]|\\.)*")(\s*,\s*)("(?:[^"\\]|\\.)*")', re.S)
        m = pat.search(out)
        if not m:
            missing.append(name)
            continue
        t = json.dumps(e["title"]); d = json.dumps(e["desc"])
        new = m.group(1) + t + m.group(3) + d
        if new != m.group(0):
            out = out[:m.start()] + new + out[m.end():]
            done += 1
    if write and done:
        open(fp, "w", encoding="utf-8").write(out)
    return done, missing


def main():
    write = "--write" in sys.argv
    trimmed = "--trimmed" in sys.argv
    plan = json.load(open(os.path.join(HERE, "data", "meta_plan.json"), encoding="utf-8"))["entries"]

    rows = []
    for e in plan:
        desc = e["description_trimmed"] if trimmed else e["description"]
        fp = resolve(e["path"])
        if not fp:
            sys.exit(f"no file for {e['path']}")
        rows.append({"page": e["page"], "path": e["path"], "file": fp,
                     "title": e["title"], "desc": desc})

    mode = "TRIMMED (stock endings removed)" if trimmed else "VERBATIM (exactly as the sheet)"
    print(f"{'APPLYING' if write else 'DRY RUN'} — {mode}\n")

    changed = 0
    for r in rows:
        if update_html(r["file"], r["title"], r["desc"], write):
            changed += 1
    print(f"[1/3] HTML files            : {changed}/{len(rows)} would change"
          if not write else f"[1/3] HTML files            : {changed}/{len(rows)} updated")

    by_slug = {}
    for r in rows:
        if not r["path"].startswith("/services/") or r["path"] == "/services/":
            continue
        slug = r["path"].strip("/").split("/")[-1] + ".html"
        by_slug[SLUG_FIX.get(slug, slug)] = r
    n_svc, unmatched = update_services_data(by_slug, write)
    print(f"[2/3] services_data.py      : {n_svc}/{len(by_slug)} entries"
          + (f"  UNMATCHED: {sorted(unmatched)}" if unmatched else ""))

    by_name = {}
    for r in rows:
        rel = os.path.relpath(r["file"], SITE)
        by_name[BUILD_NAME.get(rel, rel)] = r
    n_core, missing = update_build_py(by_name, write)
    print(f"[3/3] build.py write() calls: {n_core} updated"
          + (f"  (not in build.py: {len(missing)} — hand-written pages)" if missing else ""))

    over = [r for r in rows if len(r["desc"]) > 156]
    print(f"\ndescriptions over 156 chars : {len(over)}/{len(rows)}"
          + ("  <- Google will truncate these" if over else ""))
    if not write:
        print("\nNothing written. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
