#!/usr/bin/env python3
"""Parse DV Service Pages Content.docx text dump into structured Python data
for build.py to render. Emits site/services_data.py.

Input:  /tmp/dv_services.txt (text-extracted from the docx)
Output: /Users/poojanvig/dv/site/services_data.py
"""
import os
import re
import pprint
from pathlib import Path

DOC_TXT = Path("/tmp/dv_services.txt")
OUT = Path("/Users/poojanvig/dv/site/services_data.py")

# ---------- Slug mapping (doc slug -> site filename) -----------------
# Existing 11 site pages keep their slugs; new 30 derive from doc slug.
DOC_TO_SITE_SLUG = {
    "/SEO": "seo.html",
    "/SOCIAL-MEDIA-MANAGEMENT": "social-media-management.html",
    "/INFLUENCER-MARKETING": "influencer-marketing.html",
    "/DIGITAL-PR": "digital-pr.html",
    "/ONLINE-REPUTATION-MANAGEMENT": "online-reputation-management.html",
    "/CONTENT-MARKETING": "organic-marketing-services.html",
    "/UI-UX-DESIGN": "ui-ux-design.html",
    "/PRODUCT-DESIGN": "product-design.html",
    "/BRAND-IDENTITY": "branding-and-design.html",
    "/COMMUNICATION-DESIGN": "communication-design.html",
    "/CONTENT-COPY-WRITING": "content-copy-writing.html",
    "/SEARCH-PPC": "pay-per-click.html",
    "/DISPLAY-ADVERTISING": "display-advertising.html",
    "/FACEBOOK-INSTAGRAM-ADVERTISING": "facebook-instagram-advertising.html",
    "/SHOPPING-ADS": "shopping-ads.html",
    "/SOCIAL-MEDIA-ADVERTISING": "paid-social-media-advertising.html",
    "/AMAZON-MARKETING": "amazon-marketing.html",
    "/CRO": "conversion-rate-optimisation.html",
    "/REVENUE-GENERATION": "revenue-generation.html",
    "/LEAD-GENERATION": "lead-generation.html",
    "/CMO-CONSULTANCY": "cmo-consultancy.html",
    "/LANDING-PAGES": "landing-page-design.html",
    "/REAL-ESTATE-LEAD-GENERATION": "real-estate-lead-generation.html",
    "/RESEARCH-INSIGHTS": "research-and-insights.html",
    "/STRATEGY-PLANNING": "strategy-and-planning.html",
    "/ANALYTICS-CONFIGURATION": "analytics-configuration.html",
    "/GOOGLE-TAG-MANAGER": "google-tag-manager.html",
    "/DATA-STRATEGY": "data-strategy-consulting-services.html",
    "/WEBSITE-DEVELOPMENT": "website-development.html",
    "/CUSTOM-SOFTWARE": "custom-software-development.html",
    "/ECOMMERCE-DEVELOPMENT": "ecommerce-development.html",
    "/WORDPRESS-DEVELOPMENT": "wordpress-development.html",
    "/MOBILE-APPS": "mobile-app-development.html",
    "/LINUX-HOSTING": "linux-hosting.html",
    "/BUSINESS-EMAIL": "business-email.html",
    "/WHATSAPP-MARKETING": "whatsapp-marketing-services.html",
    "/PERFORMANCE-MARKETING": "performance-marketing-agency.html",
    "/NATIVE-ADVERTISING": "native-advertising.html",
    "/ECOMMERCE-MARKETING": "ecommerce-marketing.html",
    "/CRM-SERVICES": "crm-services.html",
    "/GEO-OPTIMIZATION": "generative-search-optimisation.html",
}

# Category groupings for nav mega-menu and services hub grid.
# (category, [doc_slugs in display order])
CATEGORIES = [
    ("Marketing", [
        "/SEO",
        "/SOCIAL-MEDIA-MANAGEMENT",
        "/INFLUENCER-MARKETING",
        "/DIGITAL-PR",
        "/ONLINE-REPUTATION-MANAGEMENT",
        "/CONTENT-MARKETING",
        "/WHATSAPP-MARKETING",
        "/PERFORMANCE-MARKETING",
        "/ECOMMERCE-MARKETING",
        "/GEO-OPTIMIZATION",
    ]),
    ("Advertising", [
        "/SEARCH-PPC",
        "/DISPLAY-ADVERTISING",
        "/FACEBOOK-INSTAGRAM-ADVERTISING",
        "/SHOPPING-ADS",
        "/SOCIAL-MEDIA-ADVERTISING",
        "/AMAZON-MARKETING",
        "/NATIVE-ADVERTISING",
    ]),
    ("Design & Content", [
        "/UI-UX-DESIGN",
        "/PRODUCT-DESIGN",
        "/BRAND-IDENTITY",
        "/COMMUNICATION-DESIGN",
        "/CONTENT-COPY-WRITING",
    ]),
    ("Strategy & Data", [
        "/CRO",
        "/REVENUE-GENERATION",
        "/LEAD-GENERATION",
        "/CMO-CONSULTANCY",
        "/LANDING-PAGES",
        "/REAL-ESTATE-LEAD-GENERATION",
        "/RESEARCH-INSIGHTS",
        "/STRATEGY-PLANNING",
        "/ANALYTICS-CONFIGURATION",
        "/GOOGLE-TAG-MANAGER",
        "/DATA-STRATEGY",
    ]),
    ("Tech & Development", [
        "/WEBSITE-DEVELOPMENT",
        "/CUSTOM-SOFTWARE",
        "/ECOMMERCE-DEVELOPMENT",
        "/WORDPRESS-DEVELOPMENT",
        "/MOBILE-APPS",
        "/LINUX-HOSTING",
        "/BUSINESS-EMAIL",
        "/CRM-SERVICES",
    ]),
]

# Card icon + short blurb for the services hub grid (one per service)
CARD_META = {
    "/SEO":                          ("seo",        "Rank, engage, and grow with on-page, technical and content SEO."),
    "/SOCIAL-MEDIA-MANAGEMENT":      ("social",     "Strategy, content, community and platform-native growth across handles."),
    "/INFLUENCER-MARKETING":         ("influencer", "Vetted creators, ASCI-compliant briefs and campaigns that drive sales."),
    "/DIGITAL-PR":                   ("pr",         "Editorial coverage, thought leadership and authority-building backlinks."),
    "/ONLINE-REPUTATION-MANAGEMENT": ("orm",        "Suppress, monitor and shape your brand's online narrative."),
    "/CONTENT-MARKETING":            ("content",    "SEO-led content engines that earn rankings, links and trust."),
    "/UI-UX-DESIGN":                 ("uiux",       "Research-driven UX and UI for web, app and product teams."),
    "/PRODUCT-DESIGN":               ("product",    "End-to-end product design from discovery to launch-ready specs."),
    "/BRAND-IDENTITY":               ("brand",      "Brand strategy, identity systems and creative direction."),
    "/COMMUNICATION-DESIGN":         ("comm",       "Marketing collateral, sales enablement and brand-aligned creative."),
    "/CONTENT-COPY-WRITING":         ("copy",       "Conversion copywriting, content writing and editorial systems."),
    "/SEARCH-PPC":                   ("ppc",        "Google &amp; Bing search ads engineered for high-intent conversions."),
    "/DISPLAY-ADVERTISING":          ("display",    "Programmatic and Google Display campaigns for awareness and remarketing."),
    "/FACEBOOK-INSTAGRAM-ADVERTISING": ("meta",     "Meta Ads with creative-led, ROAS-driven campaign management."),
    "/SHOPPING-ADS":                 ("shopping",   "Google Shopping &amp; PMax for e-commerce SKU-level performance."),
    "/SOCIAL-MEDIA-ADVERTISING":     ("social",     "Paid social across Meta, LinkedIn, YouTube and emerging platforms."),
    "/AMAZON-MARKETING":             ("ecom",       "Amazon Ads, listing optimisation and marketplace growth."),
    "/NATIVE-ADVERTISING":           ("native",     "Premium native placements that earn attention without interruption."),
    "/CRO":                          ("cro",        "Experiment-led CRO that lifts conversion rates with statistical rigour."),
    "/REVENUE-GENERATION":           ("revenue",    "Full-funnel revenue programmes engineered around CAC and LTV."),
    "/LEAD-GENERATION":              ("lead",       "B2B and consumer lead-gen engines built on real attribution."),
    "/CMO-CONSULTANCY":              ("cmo",        "Fractional CMO leadership for category leaders and high-growth brands."),
    "/LANDING-PAGES":                ("page",       "High-converting landing pages built around campaign intent."),
    "/REAL-ESTATE-LEAD-GENERATION":  ("realestate", "Real-estate-specific lead engines for projects, channel partners and resale."),
    "/RESEARCH-INSIGHTS":            ("research",   "Audience, market and category research that informs strategy."),
    "/STRATEGY-PLANNING":            ("strategy",   "Marketing strategy, planning and roadmap consulting."),
    "/ANALYTICS-CONFIGURATION":      ("analytics",  "GA4, Looker Studio and event-tracking implementation done right."),
    "/GOOGLE-TAG-MANAGER":           ("gtm",        "GTM containers, server-side tagging and event governance."),
    "/DATA-STRATEGY":                ("data",       "CDP, attribution and the data stack that drives decisions."),
    "/WEBSITE-DEVELOPMENT":          ("web",        "Performance-tuned websites engineered for SEO and conversion."),
    "/CUSTOM-SOFTWARE":              ("software",   "Bespoke web apps, internal tools and integrations built around your business."),
    "/ECOMMERCE-DEVELOPMENT":        ("cart",       "Shopify, WooCommerce and headless commerce builds that convert and scale."),
    "/WORDPRESS-DEVELOPMENT":        ("wp",         "Production-grade WordPress builds with custom themes and plugins."),
    "/MOBILE-APPS":                  ("mobile",     "iOS, Android and cross-platform app development."),
    "/LINUX-HOSTING":                ("server",     "Managed Linux hosting, monitoring and infrastructure operations."),
    "/BUSINESS-EMAIL":               ("email",      "Google Workspace and Microsoft 365 setup with deliverability done right."),
    "/WHATSAPP-MARKETING":           ("whatsapp",   "Conversational commerce on the WhatsApp Business API."),
    "/PERFORMANCE-MARKETING":        ("perf",       "Full-funnel performance marketing tied to revenue, not vanity."),
    "/ECOMMERCE-MARKETING":          ("ecom",       "End-to-end e-commerce growth across marketplaces and D2C."),
    "/CRM-SERVICES":                 ("crm",        "CRM implementation, automation and lifecycle marketing."),
    "/GEO-OPTIMIZATION":             ("ai",         "Visibility in ChatGPT, Gemini, Perplexity and AI Overviews."),
}

# E-E-A-T pillar mapping (icons + label) for rendering
PILLAR_LABEL = {
    "★ Exp":   ("Experience",       "Experience"),
    "✓ Exp":   ("Expertise",        "Expertise"),
    "◆ Auth":  ("Authoritativeness","Authority"),
    "✔ Trust": ("Trustworthiness",  "Trust"),
}

# ---------- Parsing helpers ------------------------------------------

PAGE_RE = re.compile(r"^Service Page (\d+)\s+·\s+(/[A-Z0-9\-]+)\s*$")

def slurp_lines():
    raw = DOC_TXT.read_text(encoding="utf-8")
    return [l.rstrip() for l in raw.split("\n")]

def find_pages(lines):
    """Return list of (idx, num, doc_slug) markers."""
    out = []
    for i, l in enumerate(lines):
        m = PAGE_RE.match(l.strip())
        if m:
            out.append((i, int(m.group(1)), m.group(2)))
    return out

def slice_section(lines, start, end_marker_lines):
    """Return lines[start:next_index_of_any_end_marker]."""
    for j in range(start, len(lines)):
        s = lines[j].strip()
        for em in end_marker_lines:
            if s == em:
                return lines[start:j], j
    return lines[start:], len(lines)

def is_blank(s): return not s.strip()

def parse_keywords_block(lines, key_label):
    """Find a labelled list block. Looks for a line starting with `key_label:`
    then accumulates following non-blank lines until the next labelled line
    (Primary/Secondary/LSI/Meta/E-E-A-T) or blank. The first occurrence of
    key_label may itself contain values after a colon."""
    out = []
    keys_to_stop = (
        "Primary Keywords:", "Secondary Keywords:", "LSI / Semantic Keywords:",
        "Meta Title:", "Meta Description:", "E-E-A-T Focus:",
        "Keyword Strategy & On-Page Metadata", "E-E-A-T Trust Signals",
    )
    found = False
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not found:
            if s.startswith(key_label):
                found = True
                rest = s[len(key_label):].lstrip()
                if rest:
                    # Inline list separated by | or comma
                    parts = re.split(r"\s*\|\s*", rest)
                    for p in parts:
                        if p:
                            out.append(p)
                continue
        else:
            if not s:
                # blank line — terminate if we have items
                if out:
                    return out
                continue
            if any(s.startswith(k) for k in keys_to_stop):
                return out
            out.append(s)
    return out

def get_simple_field(lines, label):
    for raw in lines:
        s = raw.strip()
        if s.startswith(label):
            return s[len(label):].strip()
    return ""

def parse_eeat_signals(lines):
    """Extract the 4 EEAT pillar entries.
    The doc table is a flat sequence of lines:
        ★ Exp
        <signal name>
        <evidence paragraph>
        ✓ Exp
        ...
    Order is: pillar marker → signal name → evidence.
    Boilerplate intro/ headers ("E-E-A-T Pillar", "Trust Signal", "Evidence")
    appear once before the rows; we skip them.
    """
    rows = []
    pillar_markers = list(PILLAR_LABEL.keys())
    i = 0
    n = len(lines)
    while i < n and len(rows) < 4:
        s = lines[i].strip()
        if s in pillar_markers:
            pillar_key = s
            # find next two non-blank non-header lines
            signal = None
            evidence = None
            j = i + 1
            while j < n and (signal is None or evidence is None):
                t = lines[j].strip()
                if t and t not in ("E-E-A-T Pillar", "Trust Signal", "Evidence"):
                    if signal is None:
                        signal = t
                    elif evidence is None:
                        evidence = t
                j += 1
            if signal and evidence:
                pl_full, pl_short = PILLAR_LABEL[pillar_key]
                rows.append({"pillar": pl_full, "tag": pl_short,
                             "signal": signal, "evidence": evidence,
                             "marker": pillar_key.split()[0]})
            i = j
            continue
        i += 1
    return rows

def parse_faqs(lines):
    """FAQ section = alternating question lines and answer paragraphs.
    Skip the leading boilerplate intro paragraph that begins with
    'Common questions answered for...' """
    faqs = []
    skipped_intro = False
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if not skipped_intro and s.startswith("Common questions answered"):
            skipped_intro = True
            i += 1
            continue
        # Question candidates: end with "?"
        if s.endswith("?"):
            q = s
            # next non-blank line is the answer
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n:
                a = lines[j].strip()
                faqs.append((q, a))
                i = j + 1
                continue
        i += 1
    # Dedupe — doc has a few duplicate Qs (e.g. GEO page).
    seen = set()
    uniq = []
    for q, a in faqs:
        if q in seen:
            continue
        seen.add(q)
        uniq.append((q, a))
    return uniq[:5]  # cap at 5

def parse_schema(lines):
    """Bullet list of schema markup names."""
    out = []
    for raw in lines:
        s = raw.strip()
        if not s: continue
        # skip section header
        if s == "Recommended Schema Markup": continue
        out.append(s)
    return out

# Body classification ------------------------------------------------

EXEMPT_INTRO = (
    "The signals below demonstrate how DV Digital establishes Experience,",
)

def _looks_like_heading(line):
    """Promote the first item of a candidate run to a section heading when
    it has heading-shaped grammar (question word, possessive, or 'X We Y'
    pattern) and is short enough to plausibly be a header."""
    starters = (
        "What ", "Why ", "How ", "When ", "Where ", "Who ", "Which ",
        "Our ", "We ", "Industries ", "Frequently ", "Things ", "Common ",
        "Phase ", "Step ", "The Four ", "The Three ", "The Five ",
        "Beyond ", "Choose ", "Inside ", "Behind ", "Tools ", "Platforms ",
        "Channels ", "Categories ", "Networks ", "Types ", "Specialised ",
        "Specialized ", "Native ", "Best ", "Leading ", "Top ", "Full ",
    )
    enders = (
        " Cover", " Covers", " Provide", " Provides", " Offer", " Offers",
        " Deploy", " Deploys", " Run", " Runs", " Build", " Builds",
        " Operate On", " Specialise In", " Specialize In", " Work On",
        " Excel At", " Serve", " Serves", " Work With", " Build For",
        " Trust Us", " Choose Us", " Hire Us", " Stand Out", " Win",
        " Matters", " Differs", " Works",
        " We Build", " We Provide", " We Cover", " We Run", " We Operate",
        " We Offer", " We Excel", " We Specialise", " We Specialize",
        " We Work", " We Serve", " We Deploy", " We Deliver",
    )
    # An em-dash separator inside the line marks a "Label — body" bullet,
    # not a heading — reject those outright.
    if " — " in line or " – " in line: return False
    if line.startswith(starters):
        # Require uppercase second word too (avoids "Full transparency...")
        rest = line.split(maxsplit=1)
        if len(rest) >= 2 and rest[1] and not rest[1][0].isupper():
            return False
        return True
    if any(line.endswith(s) for s in enders):
        return True
    # Title-Case fragment (1..9 words, ≥80% capitalised first-letters).
    words = line.split()
    if 1 <= len(words) <= 9:
        upper = sum(1 for w in words if w[0].isupper())
        if upper / len(words) >= 0.8:
            return True
    return False

def classify_body(lines):
    """Turn the body region into a flat list of typed blocks: h2, p, li.
    Heuristics:
      - Skip the EEAT-table intro boilerplate paragraph.
      - A 'cand' is a non-blank line 3..130 chars without terminal . ! ?
      - In a run of 3+ consecutive cands → bullets, but PROMOTE the first
        to 'h2' when its grammar reads like a section heading.
      - Isolated cand(s) → 'h2' (section heading)
      - Anything else → 'p'
    """
    # Pre-filter: drop EEAT intro boilerplate
    cleaned = []
    for raw in lines:
        s = raw.strip()
        if any(s.startswith(p) for p in EXEMPT_INTRO):
            continue
        cleaned.append(raw)

    # First pass: tag (min length 3 so short labels like "MGID" still count)
    tags = []
    for raw in cleaned:
        s = raw.strip()
        if not s:
            tags.append(("blank", ""))
            continue
        if 3 <= len(s) <= 130 and s[-1] not in '.!?':
            tags.append(("cand", s))
        else:
            tags.append(("para", s))

    # Sub-heading marker: "Phase 1 — X" / "Step 02 — X" / "Tier 3 — X"
    h3_prefix_re = re.compile(
        r'^(Phase|Step|Tier|Stage|Module|Level|Track)\s+\w{1,4}\s*[—–:\-]',
        re.IGNORECASE,
    )

    # Second pass: collapse runs of 3+ cands into 'li' (with optional heading)
    out = []
    i = 0
    n = len(tags)
    while i < n:
        kind, text = tags[i]
        if kind == "blank":
            i += 1
            continue
        if kind == "cand":
            run_idx = []
            j = i
            while j < n and tags[j][0] in ("cand", "blank"):
                if tags[j][0] == "cand":
                    run_idx.append(j)
                j += 1
            if len(run_idx) >= 3:
                # Promote any heading-shaped item to h2 (handles cases where
                # the doc stacks multiple "Heading + bullet list" blocks back
                # to back without paragraph breaks between them).
                for k in run_idx:
                    text = tags[k][1]
                    if _looks_like_heading(text):
                        kind = "h3" if h3_prefix_re.match(text) else "h2"
                        out.append((kind, text))
                    else:
                        out.append(("li", text))
            else:
                for k in run_idx:
                    text = tags[k][1]
                    kind = "h3" if h3_prefix_re.match(text) else "h2"
                    out.append((kind, text))
            i = j
            continue
        out.append(("p", text))
        i += 1
    return out

# ---------- Per-page parser ------------------------------------------

def parse_page(lines, start, end):
    """lines[start:end] cover one service page including the marker line."""
    block = lines[start:end]
    # block[0] is "Service Page N · /SLUG"
    m = PAGE_RE.match(block[0].strip())
    num = int(m.group(1))
    doc_slug = m.group(2)
    # H1 is the next non-blank line
    i = 1
    while i < len(block) and not block[i].strip():
        i += 1
    h1 = block[i].strip()
    # ---- find section boundaries ----
    def find_idx(text, after=0):
        for j in range(after, len(block)):
            if block[j].strip() == text:
                return j
        return -1

    kw_start = find_idx("Keyword Strategy & On-Page Metadata")
    eeat_start = find_idx("E-E-A-T Trust Signals")
    faq_start = find_idx("Frequently Asked Questions")
    schema_start = find_idx("Recommended Schema Markup")

    if kw_start < 0 or eeat_start < 0 or faq_start < 0:
        raise ValueError(f"Page {num} {doc_slug}: missing required sections")

    kw_block = block[kw_start+1:eeat_start]
    eeat_block = block[eeat_start+1:]
    # cut eeat_block at next major header (the body starts after the 4 pillar rows)
    # Body region: after EEAT signals (and intro paragraph) up to FAQ
    body_start = eeat_start + 1
    body_block_full = block[body_start:faq_start]
    faq_block = block[faq_start+1:schema_start if schema_start > 0 else len(block)]
    schema_block = block[schema_start+1:] if schema_start > 0 else []

    # Parse keyword metadata
    primary_kw = get_simple_field(kw_block, "Primary Keywords:")
    secondary_kw = parse_keywords_block(kw_block, "Secondary Keywords:")
    lsi_kw = parse_keywords_block(kw_block, "LSI / Semantic Keywords:")
    meta_title = get_simple_field(kw_block, "Meta Title:")
    meta_desc = get_simple_field(kw_block, "Meta Description:")
    eeat_focus = get_simple_field(kw_block, "E-E-A-T Focus:")

    # Parse EEAT signals (use full body which has the table at top)
    eeat_signals = parse_eeat_signals(body_block_full)

    # Strip EEAT table rows from body before classifying
    eeat_consumed_until = 0
    rows_seen = 0
    pillar_markers = list(PILLAR_LABEL.keys())
    for k, raw in enumerate(body_block_full):
        s = raw.strip()
        if s in pillar_markers:
            rows_seen += 1
            # signal + evidence consume the next two non-blank lines
            need = 2
            kk = k + 1
            while kk < len(body_block_full) and need:
                ts = body_block_full[kk].strip()
                if ts and ts not in ("E-E-A-T Pillar", "Trust Signal", "Evidence"):
                    need -= 1
                kk += 1
            eeat_consumed_until = kk
            if rows_seen == 4:
                break
    body_after_eeat = body_block_full[eeat_consumed_until:]

    body_blocks = classify_body(body_after_eeat)

    # Parse FAQs
    faqs = parse_faqs(faq_block)

    # Parse schema
    schema = parse_schema(schema_block)

    # Choose intro: use the first 'p' of body as the hero intro/lead.
    intro = ""
    intro_idx = -1
    for k, (t, txt) in enumerate(body_blocks):
        if t == "p":
            intro = txt
            intro_idx = k
            break
    body_after_intro = body_blocks[intro_idx+1:] if intro_idx >= 0 else body_blocks

    return {
        "num": num,
        "doc_slug": doc_slug,
        "site_slug": DOC_TO_SITE_SLUG[doc_slug],
        "h1": h1,
        "primary_kw": primary_kw,
        "secondary_kw": secondary_kw,
        "lsi_kw": lsi_kw,
        "meta_title": meta_title,
        "meta_desc": meta_desc,
        "eeat_focus": eeat_focus,
        "eeat_signals": eeat_signals,
        "intro": intro,
        "blocks": body_after_intro,
        "faqs": faqs,
        "schema": schema,
    }

# ---------- Driver ----------------------------------------------------

def main():
    lines = slurp_lines()
    pages = find_pages(lines)
    assert len(pages) == 41, f"Expected 41 pages, found {len(pages)}"

    parsed = []
    for k, (idx, num, slug) in enumerate(pages):
        end = pages[k+1][0] if k+1 < len(pages) else len(lines)
        try:
            data = parse_page(lines, idx, end)
            parsed.append(data)
        except Exception as e:
            print(f"  ! page {num} {slug}: {e}")
            raise

    # Sanity checks
    for p in parsed:
        if not p["faqs"]:
            print(f"  ! page {p['num']} {p['doc_slug']}: no FAQs parsed")
        if not p["eeat_signals"] or len(p["eeat_signals"]) != 4:
            print(f"  ! page {p['num']} {p['doc_slug']}: parsed {len(p['eeat_signals'])} EEAT rows")
        if not p["intro"]:
            print(f"  ! page {p['num']} {p['doc_slug']}: no intro paragraph")

    # Emit Python module
    header = '''"""Auto-generated by parse_services.py — do not edit by hand.
Source: DV Service Pages Content.docx → /tmp/dv_services.txt → this module.
"""
'''
    body = "SERVICES = " + pprint.pformat(parsed, width=120, sort_dicts=False) + "\n\n"
    body += "CATEGORIES = " + pprint.pformat(CATEGORIES_AS_SLUGS(parsed), width=120, sort_dicts=False) + "\n\n"
    body += "CARD_META = " + pprint.pformat(CARD_META, width=120, sort_dicts=False) + "\n"
    OUT.write_text(header + body, encoding="utf-8")
    print(f"Wrote {OUT} with {len(parsed)} services")

def CATEGORIES_AS_SLUGS(parsed):
    """Re-emit CATEGORIES with site-slugs (for use by build.py)."""
    out = []
    for cat, doc_slugs in CATEGORIES:
        site_slugs = [DOC_TO_SITE_SLUG[ds] for ds in doc_slugs]
        out.append((cat, site_slugs))
    return out

if __name__ == "__main__":
    main()
