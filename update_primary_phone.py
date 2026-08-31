#!/usr/bin/env python3
"""Replace the primary contact number 9956655662 with 8850934184.

The number appears in four distinct shapes and each has to be replaced in
kind, or tel: links and WhatsApp deep links break:

    +919956655662     tel: hrefs
    +91-9956655662    schema.org telephone
    919956655662      wa.me deep links (no plus)
    99566 55662       human-readable display text

The secondary number 7045337060 is left alone.
"""
from pathlib import Path

OLD, NEW = "9956655662", "8850934184"
SUBS = [
    (f"+91{OLD}",  f"+91{NEW}"),                      # tel: href
    (f"+91-{OLD}", f"+91-{NEW}"),                     # schema
    (f"91{OLD}",   f"91{NEW}"),                       # wa.me
    ("99566 55662", "88509 34184"),                   # display
    (OLD, NEW),                                       # any bare leftover
]

ROOT = Path(__file__).resolve().parent
EXT = {".html", ".json", ".txt", ".xml", ".js", ".py", ".gs"}

files = [p for p in ROOT.rglob("*")
         if p.is_file() and p.suffix in EXT and ".git" not in p.parts
         and p.name != Path(__file__).name]

n_files = 0
counts = {a: 0 for a, _ in SUBS}
for p in files:
    try: s = p.read_text(encoding="utf-8")
    except Exception: continue
    if OLD not in s and "99566 55662" not in s:
        continue
    before = s
    for a, b in SUBS:
        c = s.count(a)
        if c:
            counts[a] += c
            s = s.replace(a, b)
    if s != before:
        p.write_text(s, encoding="utf-8"); n_files += 1

print(f"  files updated: {n_files}")
for a, c in counts.items():
    if c: print(f"    {a:<18} -> {c}")
