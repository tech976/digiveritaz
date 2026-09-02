"""
Yoast-style on-page SEO + readability engine for DigiVeritaz.

Pure stdlib, no third-party packages -- so Vercel builds the function cleanly
and `python3 serve.py` runs it locally with nothing installed.

Split in two halves on purpose:
  parse_html(html)         -> a PageFacts bag of raw observations
  analyze(url, html, kp)   -> the scored report the dashboard renders

The underscore prefix keeps Vercel from publishing this as a route, matching
the existing site/api/_otp.js convention.
"""
import re, json, math, html as _html, urllib.request, urllib.parse, time
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; DigiVeritazSEOBot/1.0; +https://www.digiveritaz.com)"
HTTP_TIMEOUT = 8  # stay under Vercel Hobby's 10s ceiling

# Blocks whose text never counts as page copy.
_SKIP_TEXT = {"script", "style", "noscript", "template", "svg", "select", "option"}
# Landmarks stripped from the content region (nav chrome, not copy).
_CHROME = {"nav", "header", "footer", "aside"}


# ---------------------------------------------------------------- html parsing
class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.metas = {}          # name/property -> content
        self.canonical = None
        self.lang = None
        self.jsonld = []
        self.headings = []       # (level, text, in_main)
        self.paragraphs = []     # text, main only
        self.flow = []           # ordered ("h",lvl,text) / ("p",text) inside <main>
        self.images = []         # {src, alt, in_main}
        self.links = []          # {href, text, rel, in_main}
        self.main_text = []
        self.body_text = []
        self._skip_depth = 0
        self._in_jsonld = False
        self._jsonld_buf = []
        self._main_depth = 0     # >0 => inside <main>
        self._chrome_depth = 0   # >0 => inside nav/header/footer/aside
        self._h = None           # (level, [parts])
        self._p = None           # [parts]
        self._a = None           # dict + [parts]
        self._stack = []

    # -- helpers
    @property
    def _in_main(self):
        return self._main_depth > 0 and self._chrome_depth == 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._stack.append(tag)

        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
            if key:
                self.metas.setdefault(key, a.get("content", ""))
        elif tag == "link":
            rels = (a.get("rel") or "").lower().split()
            if "canonical" in rels and not self.canonical:
                self.canonical = a.get("href")
        elif tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_buf = []

        if tag in _SKIP_TEXT:
            self._skip_depth += 1
        if tag == "main":
            self._main_depth += 1
        if tag in _CHROME:
            self._chrome_depth += 1

        if tag == "img":
            self.images.append({
                "src": a.get("src") or a.get("data-src") or "",
                "alt": a.get("alt"),
                "in_main": self._in_main,
            })
        elif tag == "a":
            self._a = {"href": a.get("href") or "", "rel": (a.get("rel") or ""),
                       "in_main": self._in_main, "_t": []}
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._h = (int(tag[1]), [])
        elif tag == "p":
            self._p = []

    def handle_endtag(self, tag):
        if tag in _SKIP_TEXT and self._skip_depth:
            self._skip_depth -= 1
        if tag == "main" and self._main_depth:
            self._main_depth -= 1
        if tag in _CHROME and self._chrome_depth:
            self._chrome_depth -= 1

        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            raw = "".join(self._jsonld_buf).strip()
            if raw:
                try:
                    self.jsonld.append(json.loads(raw))
                except Exception:
                    self.jsonld.append({"_unparseable": raw[:200]})
        elif tag == "a" and self._a is not None:
            self._a["text"] = _clean(" ".join(self._a.pop("_t")))
            self.links.append(self._a)
            self._a = None
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._h is not None:
            lvl, parts = self._h
            txt = _clean(" ".join(parts))
            self.headings.append((lvl, txt, self._in_main))
            if txt and self._in_main:
                self.flow.append(("h", lvl, txt))
            self._h = None
        elif tag == "p" and self._p is not None:
            t = _clean(" ".join(self._p))
            if t and self._in_main:
                self.paragraphs.append(t)
                self.flow.append(("p", 0, t))
            self._p = None

        if self._stack and tag in self._stack:
            while self._stack:
                if self._stack.pop() == tag:
                    break

    def handle_data(self, d):
        if self._in_jsonld:
            self._jsonld_buf.append(d)
            return
        if self._in_title:
            self.title = ((self.title or "") + d)
            return
        if self._skip_depth:
            return
        if not d.strip():
            return
        if self._h is not None:
            self._h[1].append(d)
        if self._p is not None:
            self._p.append(d)
        if self._a is not None:
            self._a["_t"].append(d)
        self.body_text.append(d)
        if self._in_main:
            self.main_text.append(d)


def _clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def parse_html(html_str):
    p = _Parser()
    try:
        p.feed(html_str)
    except Exception:
        pass  # tolerate malformed markup; keep whatever we parsed
    main = _clean(" ".join(p.main_text))
    return {
        "title": _clean(p.title),
        "metas": p.metas,
        "canonical": p.canonical,
        "lang": p.lang,
        "jsonld": p.jsonld,
        "headings": p.headings,
        "paragraphs": p.paragraphs,
        "flow": p.flow,
        "images": p.images,
        "links": p.links,
        "content": main or _clean(" ".join(p.body_text)),
        "used_main": bool(main),
    }


# ------------------------------------------------------------------ linguistics
# Python's re forbids variable-width lookbehind, so abbreviation dots are masked
# to \x00 before splitting and restored afterwards.
_ABBREV = ("mr","mrs","ms","dr","prof","sr","jr","st","vs","etc","e.g","i.e","inc","ltd",
           "co","no","fig","vol","approx","pvt","ph.d","u.s","u.k")
_ABBREV_RE = re.compile(r"\b(" + "|".join(re.escape(a) for a in _ABBREV) + r")\.", re.I)
_SENT_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z0-9])")

# Yoast's transition-word families (English), trimmed to the common set.
TRANSITIONS = {
    "accordingly","additionally","afterward","afterwards","albeit","also","although","altogether",
    "another","basically","because","before","besides","but","certainly","chiefly","comparatively",
    "consequently","conversely","correspondingly","despite","doubtedly","during","emphatically",
    "equally","especially","eventually","evidently","explicitly","finally","firstly","for example",
    "for instance","further","furthermore","generally","hence","henceforth","however","in addition",
    "in brief","in conclusion","in contrast","in fact","in other words","in particular","in short",
    "in summary","in the meantime","indeed","instead","last","lastly","later","likewise","markedly",
    "meanwhile","moreover","namely","nevertheless","nonetheless","nor","notably","now","obviously",
    "occasionally","of course","on the contrary","on the other hand","otherwise","overall",
    "particularly","previously","rather","regardless","secondly","similarly","simultaneously",
    "since","so","soon","specifically","still","subsequently","surely","that is","then","thereafter",
    "therefore","thirdly","though","thus","to summarise","to summarize","too","ultimately",
    "undoubtedly","unless","unlike","until","what is more","whereas","while","yet",
}
_BE = r"(?:am|is|are|was|were|be|been|being|get|gets|got|gotten)"
_IRREGULAR_PP = (
    "born|beaten|become|begun|bent|bound|bitten|bled|blown|broken|brought|built|burnt|bought|caught|"
    "chosen|come|cost|cut|dealt|done|drawn|driven|drunk|eaten|fallen|fed|felt|fought|found|flown|"
    "forgotten|forgiven|frozen|given|gone|grown|hung|heard|hidden|hit|held|hurt|kept|known|laid|led|"
    "left|lent|let|lost|made|meant|met|paid|put|read|ridden|rung|risen|run|said|seen|sold|sent|set|"
    "shaken|shone|shot|shown|shut|sung|sunk|sat|slept|slid|spoken|spent|split|spread|stood|stolen|"
    "stuck|struck|sworn|swept|swum|taken|taught|torn|told|thought|thrown|understood|woken|worn|won|"
    "written"
)
_PASSIVE = re.compile(
    r"\b" + _BE + r"\b(?:\s+\w+ly)?\s+(?:\w+ed|" + _IRREGULAR_PP + r")\b", re.I)


def sentences(text):
    text = _clean(text)
    if not text:
        return []
    masked = _ABBREV_RE.sub(lambda m: m.group(1) + "\x00", text)
    out = [s.replace("\x00", ".").strip() for s in _SENT_SPLIT.split(masked)]
    return [s for s in out if s]


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text or "")


def syllables(word):
    """Vowel-group heuristic; good enough for Flesch at page scale."""
    w = re.sub(r"[^a-z]", "", (word or "").lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    n = len(re.findall(r"[aeiouy]{1,2}", w))
    return max(1, n)


def flesch_reading_ease(text):
    ss, ws = sentences(text), words(text)
    if not ss or not ws:
        return None
    syl = sum(syllables(w) for w in ws)
    score = 206.835 - 1.015 * (len(ws) / len(ss)) - 84.6 * (syl / len(ws))
    return round(max(0.0, min(100.0, score)), 1)


def passive_ratio(text):
    ss = sentences(text)
    if not ss:
        return None, 0, 0
    hits = sum(1 for s in ss if _PASSIVE.search(s))
    return round(100.0 * hits / len(ss), 1), hits, len(ss)


def transition_ratio(text):
    ss = sentences(text)
    if not ss:
        return None, 0, 0
    hits = 0
    for s in ss:
        low = " " + re.sub(r"[^a-z ]", " ", s.lower()) + " "
        low = re.sub(r"\s+", " ", low)
        if any((" " + t + " ") in low for t in TRANSITIONS):
            hits += 1
    return round(100.0 * hits / len(ss), 1), hits, len(ss)


def consecutive_starts(text, run=3):
    """Yoast flags 3+ consecutive sentences opening with the same word."""
    ss = sentences(text)
    worst, cur, prev = 1, 1, None
    for s in ss:
        w = (words(s) or [""])[0].lower()
        if w and w == prev:
            cur += 1
            worst = max(worst, cur)
        else:
            cur = 1
        prev = w
    return worst


# Approximate Google SERP pixel width (Arial ~20px) for the title tag.
_WIDE = set("MW@%mw")
_NARROW = set("iljtfrI.,:;'|!()[]{} ")
def pixel_width(s):
    px = 0.0
    for ch in s or "":
        if ch in _WIDE:      px += 15.0
        elif ch in _NARROW:  px += 5.0
        elif ch.isupper():   px += 12.0
        elif ch.isdigit():   px += 10.0
        else:                px += 9.2
    return int(round(px))


def _norm(s):
    """Lowercase, strip punctuation/diacritic noise -- for keyphrase matching."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())).strip()


def kp_hits(keyphrase, text):
    """Count keyphrase occurrences, allowing the words to be separated by up to
    two filler words (Yoast counts these as matches too)."""
    kw = _norm(keyphrase).split()
    hay = _norm(text)
    if not kw or not hay:
        return 0
    if len(kw) == 1:
        return len(re.findall(r"\b" + re.escape(kw[0]) + r"\b", hay))
    gap = r"(?:\s+\w+){0,2}\s+"
    pat = r"\b" + gap.join(re.escape(w) for w in kw) + r"\b"
    return len(re.findall(pat, hay))


# ------------------------------------------------------------------ assessments
GOOD, OK, BAD, NA = "good", "ok", "bad", "na"
_POINTS = {GOOD: 9, OK: 6, BAD: 3}


class _Report:
    """Collects bullets and rolls them into Yoast-style 0-100 group scores."""
    def __init__(self):
        self.checks = []

    def add(self, group, cid, label, status, text, weight=1, value=None):
        self.checks.append({"group": group, "id": cid, "label": label,
                            "status": status, "text": text,
                            "weight": weight, "value": value})

    def score(self, group):
        rel = [c for c in self.checks if c["group"] == group and c["status"] in _POINTS]
        if not rel:
            return None
        got = sum(_POINTS[c["status"]] * c["weight"] for c in rel)
        top = sum(9 * c["weight"] for c in rel)
        return int(round(100.0 * got / top))

    def counts(self, group=None):
        rel = [c for c in self.checks if group is None or c["group"] == group]
        return {s: sum(1 for c in rel if c["status"] == s) for s in (GOOD, OK, BAD, NA)}


def _band(v, good, ok):
    """good/ok are predicates; returns a bullet status."""
    return GOOD if good(v) else (OK if ok(v) else BAD)


def analyze(url, html_str, keyphrase=None, status_code=200, fetch_ms=None,
            keyphrase_source="derived", synonyms=None):
    f = parse_html(html_str)
    r = _Report()
    synonyms = synonyms or []

    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc.lower().replace("www.", "")
    slug = parsed_url.path.strip("/").split("/")[-1] or "home"

    content = f["content"]
    ws = words(content)
    wc = len(ws)
    title = f["title"] or ""
    metas = f["metas"]
    desc = _clean(metas.get("description", ""))
    kp = _clean(keyphrase or "")

    # ---------------------------------------------------------------- SEO group
    G = "seo"

    if not kp:
        r.add(G, "keyphrase_set", "Focus keyphrase", NA,
              "No focus keyphrase set for this page, so keyphrase checks are skipped.")
    else:
        n_kw = len(_norm(kp).split())
        r.add(G, "keyphrase_length", "Keyphrase length",
              GOOD if 1 <= n_kw <= 4 else OK,
              f"The focus keyphrase is {n_kw} word{'s' if n_kw != 1 else ''} long."
              + ("" if n_kw <= 4 else " Keyphrases over 4 words are hard to rank."),
              weight=1, value=n_kw)

        # Keyphrase in title, and how early it appears.
        t_norm, kp_norm = _norm(title), _norm(kp)
        if kp_hits(kp, title):
            pos = t_norm.find(kp_norm.split()[0])
            early = pos >= 0 and pos <= max(10, len(t_norm) * 0.35)
            r.add(G, "title_keyphrase", "Keyphrase in SEO title",
                  GOOD if early else OK,
                  "The focus keyphrase appears at the beginning of the SEO title." if early
                  else "The focus keyphrase is in the SEO title, but not near the beginning. "
                       "Move it to the front where possible.", weight=3)
        else:
            r.add(G, "title_keyphrase", "Keyphrase in SEO title", BAD,
                  "The focus keyphrase does not appear in the SEO title.", weight=3)

        if desc:
            r.add(G, "meta_keyphrase", "Keyphrase in meta description",
                  GOOD if kp_hits(kp, desc) else BAD,
                  "The meta description contains the focus keyphrase." if kp_hits(kp, desc)
                  else "The meta description does not contain the focus keyphrase.", weight=2)

        r.add(G, "slug_keyphrase", "Keyphrase in slug",
              GOOD if kp_hits(kp, slug.replace("-", " ")) else OK,
              f"The URL slug ({slug}) contains the focus keyphrase." if kp_hits(kp, slug.replace("-", " "))
              else f"The URL slug ({slug}) does not contain the focus keyphrase.", weight=2)

        intro = f["paragraphs"][0] if f["paragraphs"] else ""
        r.add(G, "intro_keyphrase", "Keyphrase in introduction",
              GOOD if kp_hits(kp, intro) else BAD,
              "The focus keyphrase appears in the first paragraph." if kp_hits(kp, intro)
              else "The focus keyphrase does not appear in the first paragraph. "
                   "Put it in the opening lines so readers and crawlers see it early.", weight=2)

        subs = [t for lvl, t, in_main in f["headings"] if in_main and lvl in (2, 3)]
        n_sub_hits = sum(1 for t in subs if kp_hits(kp, t))
        if not subs:
            r.add(G, "subhead_keyphrase", "Keyphrase in subheadings", BAD,
                  "This page has no H2 or H3 subheadings.", weight=2)
        else:
            r.add(G, "subhead_keyphrase", "Keyphrase in subheadings",
                  GOOD if n_sub_hits else BAD,
                  f"{n_sub_hits} of {len(subs)} subheadings contain the focus keyphrase." if n_sub_hits
                  else f"None of the {len(subs)} subheadings contain the focus keyphrase.",
                  weight=2, value=n_sub_hits)

        hits = kp_hits(kp, content)
        density = round(100.0 * hits * len(_norm(kp).split()) / wc, 2) if wc else 0.0
        if density == 0:
            d_status, d_msg = BAD, "The focus keyphrase does not appear in the page copy."
        elif density < 0.5:
            d_status, d_msg = OK, f"Keyphrase density is {density}% ({hits} occurrences) — a little low. Aim for 0.5–3%."
        elif density <= 3.0:
            d_status, d_msg = GOOD, f"Keyphrase density is {density}% ({hits} occurrences) — within the ideal 0.5–3% range."
        else:
            d_status, d_msg = BAD, f"Keyphrase density is {density}% ({hits} occurrences) — over-optimised. Keep it under 3%."
        r.add(G, "density", "Keyphrase density", d_status, d_msg, weight=3, value=density)

        alts = [i for i in f["images"] if (i.get("alt") or "").strip()]
        alt_hit = sum(1 for i in alts if kp_hits(kp, i["alt"]))
        if f["images"]:
            r.add(G, "alt_keyphrase", "Keyphrase in image alt text",
                  GOOD if alt_hit else OK,
                  f"{alt_hit} image alt attribute(s) contain the focus keyphrase." if alt_hit
                  else "No image alt text contains the focus keyphrase.", weight=1, value=alt_hit)

    # -- title tag ---------------------------------------------------------
    tpx = pixel_width(title)
    if not title:
        r.add(G, "title_width", "SEO title width", BAD, "This page has no title tag.", weight=3)
    else:
        st = _band(tpx, lambda v: 400 <= v <= 580, lambda v: 300 <= v < 400)
        r.add(G, "title_width", "SEO title width", st,
              f"The SEO title is ~{tpx}px ({len(title)} chars). "
              + ("Well within the 400–580px Google shows." if st == GOOD
                 else "Too short — you are leaving SERP space unused." if tpx < 400
                 else "Too long — Google will truncate it."), weight=3, value=tpx)

    # -- meta description --------------------------------------------------
    if not desc:
        r.add(G, "meta_desc", "Meta description", BAD,
              "No meta description. Google will invent one from the page copy.", weight=3)
    else:
        n = len(desc)
        st = _band(n, lambda v: 120 <= v <= 156, lambda v: 80 <= v < 120 or 156 < v <= 175)
        r.add(G, "meta_desc", "Meta description length", st,
              f"The meta description is {n} characters. "
              + ("Within the ideal 120–156." if st == GOOD
                 else "Too short — add detail to earn the click." if n < 120
                 else "Too long — Google will truncate it."), weight=3, value=n)

    # -- content length ----------------------------------------------------
    st = _band(wc, lambda v: v >= 600, lambda v: v >= 300)
    r.add(G, "text_length", "Content length", st,
          f"The page has {wc} words of body copy. "
          + ("Comfortably enough to rank." if wc >= 600
             else "Thin — aim for 600+ on a commercial page." if wc >= 300
             else "Too thin to compete. Aim for at least 300 words."), weight=3, value=wc)

    # -- headings ----------------------------------------------------------
    h1s = [t for lvl, t, in_main in f["headings"] if lvl == 1]
    if len(h1s) == 1:
        r.add(G, "h1", "H1 heading", GOOD, f"Exactly one H1: “{h1s[0][:80]}”.", weight=3)
    elif not h1s:
        r.add(G, "h1", "H1 heading", BAD, "This page has no H1 heading.", weight=3)
    else:
        r.add(G, "h1", "H1 heading", BAD,
              f"{len(h1s)} H1 headings found — a page should have exactly one.", weight=3, value=len(h1s))

    levels = [lvl for lvl, t, in_main in f["headings"] if in_main]
    skips = [(a, b) for a, b in zip(levels, levels[1:]) if b - a > 1]
    r.add(G, "heading_order", "Heading hierarchy",
          GOOD if not skips else OK,
          "Heading levels descend without skipping." if not skips
          else f"{len(skips)} place(s) skip a heading level (e.g. H{skips[0][0]} → H{skips[0][1]}).",
          weight=1, value=len(skips))

    # -- images ------------------------------------------------------------
    imgs = f["images"]
    if not imgs:
        r.add(G, "img_alt", "Image alt attributes", OK, "This page has no images.", weight=2)
    else:
        missing = [i for i in imgs if not (i.get("alt") or "").strip()]
        st = _band(len(missing), lambda v: v == 0, lambda v: v <= max(1, len(imgs) * 0.2))
        r.add(G, "img_alt", "Image alt attributes", st,
              f"All {len(imgs)} images have alt text." if not missing
              else f"{len(missing)} of {len(imgs)} images are missing alt text.",
              weight=2, value=len(missing))

    # -- links -------------------------------------------------------------
    internal = external = 0
    for l in f["links"]:
        h = (l.get("href") or "").strip()
        if not h or h.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        hp = urllib.parse.urlparse(h)
        if not hp.netloc or hp.netloc.lower().replace("www.", "") == host:
            internal += 1
        else:
            external += 1
    r.add(G, "internal_links", "Internal links",
          _band(internal, lambda v: v >= 3, lambda v: v >= 1),
          f"{internal} internal links found." + ("" if internal >= 3 else " Add more to spread authority."),
          weight=2, value=internal)
    r.add(G, "outbound_links", "Outbound links",
          _band(external, lambda v: v >= 1, lambda v: False),
          f"{external} outbound links found." if external
          else "No outbound links. Citing authoritative sources builds trust.",
          weight=1, value=external)

    # -- technical ---------------------------------------------------------
    r.add(G, "canonical", "Canonical URL", GOOD if f["canonical"] else BAD,
          f"Canonical set to {f['canonical']}" if f["canonical"]
          else "No canonical tag — duplicate URLs may compete with each other.",
          weight=2, value=f["canonical"])

    robots = (metas.get("robots") or "").lower()
    noindex = "noindex" in robots
    r.add(G, "indexable", "Indexability", BAD if noindex else GOOD,
          "This page is set to noindex — search engines will not list it." if noindex
          else "The page is indexable.", weight=3)

    og = [k for k in ("og:title", "og:description", "og:image") if metas.get(k)]
    r.add(G, "open_graph", "Open Graph tags",
          _band(len(og), lambda v: v == 3, lambda v: v >= 1),
          f"{len(og)} of 3 core Open Graph tags present ({', '.join(og) or 'none'}).",
          weight=1, value=len(og))

    tw = bool(metas.get("twitter:card"))
    r.add(G, "twitter", "Twitter card", GOOD if tw else OK,
          "Twitter card is configured." if tw else "No twitter:card meta tag.", weight=1)

    types = []
    for block in f["jsonld"]:
        for b in (block if isinstance(block, list) else [block]):
            if isinstance(b, dict):
                t = b.get("@type") or ""
                types += t if isinstance(t, list) else [t]
                for g in (b.get("@graph") or []):
                    if isinstance(g, dict) and g.get("@type"):
                        gt = g["@type"]
                        types += gt if isinstance(gt, list) else [gt]
    types = [t for t in types if t]
    r.add(G, "schema", "Structured data", GOOD if types else BAD,
          f"{len(f['jsonld'])} JSON-LD block(s): {', '.join(sorted(set(types))[:6])}." if types
          else "No JSON-LD structured data found.", weight=2, value=types)

    r.add(G, "lang", "Language attribute", GOOD if f["lang"] else OK,
          f"<html lang=\"{f['lang']}\">" if f["lang"] else "No lang attribute on <html>.", weight=1)
    r.add(G, "viewport", "Mobile viewport", GOOD if metas.get("viewport") else BAD,
          "Viewport meta tag present." if metas.get("viewport")
          else "No viewport meta tag — the page will not scale on mobile.", weight=2)
    r.add(G, "http", "HTTP status",
          GOOD if status_code == 200 else BAD,
          f"Responded {status_code}." + ("" if status_code == 200 else " Should be 200."),
          weight=3, value=status_code)
    return _readability(r, f, content, wc, url, kp, keyphrase_source, status_code, fetch_ms,
                        title, desc, tpx, h1s, imgs, internal, external, types)


def _readability(r, f, content, wc, url, kp, kp_source, status_code, fetch_ms,
                 title, desc, tpx, h1s, imgs, internal, external, schema_types):
    R = "readability"

    fre = flesch_reading_ease(content)
    if fre is None:
        r.add(R, "flesch", "Flesch reading ease", NA, "Not enough copy to score.")
    else:
        st = _band(fre, lambda v: v >= 60, lambda v: v >= 50)
        grade = ("very easy" if fre >= 80 else "easy" if fre >= 70 else "fairly easy" if fre >= 60
                 else "fairly difficult" if fre >= 50 else "difficult" if fre >= 30 else "very difficult")
        r.add(R, "flesch", "Flesch reading ease", st,
              f"Scores {fre} — {grade} to read." + ("" if st == GOOD else " Aim for 60+ by shortening sentences and words."),
              weight=3, value=fre)

    ss = sentences(content)
    if ss:
        long_s = [s for s in ss if len(words(s)) > 20]
        pct = round(100.0 * len(long_s) / len(ss), 1)
        st = _band(pct, lambda v: v <= 25, lambda v: v <= 35)
        r.add(R, "sentence_length", "Sentence length", st,
              f"{pct}% of sentences run over 20 words ({len(long_s)} of {len(ss)}). "
              + ("Within the 25% limit." if st == GOOD else "Break the long ones up."),
              weight=3, value=pct)

        worst = consecutive_starts(content)
        r.add(R, "consecutive", "Consecutive sentences", GOOD if worst < 3 else OK,
              "No three consecutive sentences start with the same word." if worst < 3
              else f"{worst} sentences in a row start with the same word.", weight=1, value=worst)

    paras = f["paragraphs"]
    if paras:
        longp = [p for p in paras if len(words(p)) > 150]
        st = _band(len(longp), lambda v: v == 0, lambda v: v <= 1)
        r.add(R, "paragraph_length", "Paragraph length", st,
              f"All {len(paras)} paragraphs are under 150 words." if not longp
              else f"{len(longp)} paragraph(s) exceed 150 words.", weight=2, value=len(longp))

    # Longest run of copy with no subheading breaking it up.
    run, worst_run = 0, 0
    for kind, lvl, text in f["flow"]:
        if kind == "h":
            run = 0
        else:
            run += len(words(text))
            worst_run = max(worst_run, run)
    if wc >= 300:
        st = _band(worst_run, lambda v: v <= 300, lambda v: v <= 350)
        r.add(R, "subheading_distribution", "Subheading distribution", st,
              f"Longest stretch without a subheading is {worst_run} words. "
              + ("Good." if st == GOOD else "Add a subheading to break it up."),
              weight=2, value=worst_run)

    pv, pv_hits, pv_total = passive_ratio(content)
    if pv is not None:
        st = _band(pv, lambda v: v <= 10, lambda v: v <= 15)
        r.add(R, "passive_voice", "Passive voice", st,
              f"{pv}% of sentences use passive voice ({pv_hits} of {pv_total}). "
              + ("Under the 10% limit." if st == GOOD else "Rewrite some in the active voice."),
              weight=2, value=pv)

    tr, tr_hits, tr_total = transition_ratio(content)
    if tr is not None:
        st = _band(tr, lambda v: v >= 30, lambda v: v >= 20)
        r.add(R, "transition_words", "Transition words", st,
              f"{tr}% of sentences contain a transition word ({tr_hits} of {tr_total}). "
              + ("Above the 30% target." if st == GOOD else "Add more to improve flow."),
              weight=2, value=tr)

    seo_score, read_score = r.score("seo"), r.score("readability")
    parts = [s for s in (seo_score, read_score) if s is not None]
    overall = int(round(sum(parts) / len(parts))) if parts else None

    return {
        "url": url,
        "status": status_code,
        "fetch_ms": fetch_ms,
        "keyphrase": kp or None,
        "keyphrase_source": kp_source,
        "scores": {"seo": seo_score, "readability": read_score, "overall": overall},
        "grade": grade_of(overall),
        "counts": r.counts(),
        "counts_seo": r.counts("seo"),
        "counts_readability": r.counts("readability"),
        "facts": {
            "title": title, "title_px": tpx, "title_chars": len(title),
            "meta_description": desc, "meta_chars": len(desc),
            "word_count": wc, "h1": h1s[0] if h1s else None, "h1_count": len(h1s),
            "headings": len([h for h in f["headings"] if h[2]]),
            "images": len(imgs),
            "images_no_alt": len([i for i in imgs if not (i.get("alt") or "").strip()]),
            "internal_links": internal, "external_links": external,
            "canonical": f["canonical"], "lang": f["lang"],
            "schema_types": sorted(set(schema_types)),
            "flesch": fre, "used_main": f["used_main"],
        },
        "checks": r.checks,
    }


def grade_of(score):
    if score is None:      return "unknown"
    if score >= 80:        return "good"
    if score >= 55:        return "ok"
    return "bad"


# ---------------------------------------------------------------------- fetching
def fetch(url, timeout=HTTP_TIMEOUT):
    """Returns (status, html, elapsed_ms, error)."""
    t0 = time.time()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-GB,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            ms = int((time.time() - t0) * 1000)
            return resp.status, raw.decode(charset, "replace"), ms, None
    except urllib.error.HTTPError as e:
        ms = int((time.time() - t0) * 1000)
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body, ms, None
    except Exception as e:
        return 0, "", int((time.time() - t0) * 1000), str(e)


def analyze_url(url, keyphrase=None, keyphrase_source="derived", timeout=HTTP_TIMEOUT):
    status, html_str, ms, err = fetch(url, timeout)
    if err or not html_str:
        return {"url": url, "status": status, "fetch_ms": ms, "error": err or "empty response",
                "scores": {"seo": None, "readability": None, "overall": None},
                "grade": "unknown", "checks": [], "counts": {}, "facts": {}}
    return analyze(url, html_str, keyphrase, status, ms, keyphrase_source)
