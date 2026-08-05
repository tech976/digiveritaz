# -*- coding: utf-8 -*-
"""Build /search-index.json — one entry per page, with its sections, for the header search."""
import io, os, re, sys, json, html
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
OUT = os.path.join(ROOT, 'search-index.json')

SKIP_FILES = {'google86ad99dbc298dc03.html', 'thank-you.html', '404.html'}
SKIP_DIRS = {'api', 'node_modules', '__pycache__', 'assets', 'css', 'js'}

def R(p):
    return io.open(p, encoding='utf-8', errors='replace').read()

def txt(s):
    s = re.sub(r'<(script|style|svg|noscript)\b.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def url_for(rel):
    rel = rel.replace('\\', '/')
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')]
    return '/' + rel[:-len('.html')] + '/'

def kind_for(rel, url):
    if rel.startswith('blog/'):
        return 'Blog'
    if rel.startswith('case-study/'):
        return 'Case study'
    if rel.startswith('uk/'):
        return 'UK'
    if url.startswith('/digital-marketing-agency-in-'):
        return 'Location'
    if rel in ('index.html', 'about-us.html', 'contact-us.html', 'faq.html', 'services.html',
               'careers.html', 'ai-news.html', 'privacy-policy.html', 'terms-and-conditions.html'):
        return 'Page'
    return 'Service'

pages = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    for f in sorted(filenames):
        if not f.endswith('.html') or f in SKIP_FILES:
            continue
        full = os.path.join(dirpath, f)
        rel = os.path.relpath(full, ROOT).replace('\\', '/')
        s = R(full)
        if re.search(r'<meta name="robots" content="[^"]*noindex', s, re.I):
            continue

        m = re.search(r'<title>(.*?)</title>', s, re.S)
        title = txt(m.group(1)) if m else ''
        title = re.sub(r'\s*\|\s*DigiVeritaz.*$', '', title).strip() or rel
        m = re.search(r'<meta name="description" content="([^"]*)"', s)
        desc = html.unescape(m.group(1)).strip() if m else ''

        body = re.search(r'<main[^>]*>(.*?)</main>', s, re.S)
        body = body.group(1) if body else s
        # drop the nav mega-menu / footer leftovers if <main> was missing
        body = re.sub(r'<(header|footer)\b.*?</\1>', ' ', body, flags=re.S | re.I)

        h1 = txt(re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S).group(1)) if re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S) else title

        # sections: each h2/h3 plus the text that follows it, up to the next heading
        secs = []
        parts = re.split(r'<h([23])[^>]*>(.*?)</h\1>', body, flags=re.S)
        # parts = [pre, level, heading, content, level, heading, content, ...]
        for i in range(1, len(parts) - 2, 3):
            heading = txt(parts[i + 1])
            content = txt(parts[i + 2])
            if not heading or len(heading) > 160:
                continue
            if re.match(r'^(related|explore more|ready to|share)\b', heading, re.I):
                continue
            secs.append({'h': heading, 't': content[:170]})
        # de-dup by heading, cap per page
        seen, out = set(), []
        for x in secs:
            k = x['h'].lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(x)
            if len(out) >= 10:
                break

        intro = ''
        for p in re.findall(r'<p[^>]*>(.*?)</p>', body, re.S):
            t = txt(p)
            if 60 <= len(t):
                intro = t[:200]
                break

        pages.append({
            'u': url_for(rel),
            'ti': title,
            'h1': h1 if h1 != title else '',
            'd': desc[:200],
            'k': kind_for(rel, url_for(rel)),
            'i': intro,
            's': out,
        })

pages.sort(key=lambda p: (p['k'] != 'Page', p['u']))
data = {'v': 1, 'n': len(pages), 'p': pages}
io.open(OUT, 'w', encoding='utf-8', newline='').write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
kb = os.path.getsize(OUT) / 1024
print('pages indexed :', len(pages))
from collections import Counter
for k, n in Counter(p['k'] for p in pages).most_common():
    print('   %-12s %d' % (k, n))
print('sections total:', sum(len(p['s']) for p in pages))
print('index size    : %.1f KB' % kb)
