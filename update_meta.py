#!/usr/bin/env python3
"""One-shot meta-tag updater for the DigiVeritaz static site.

Updates, atomically:
  1. site/services_data.py   — meta_title / meta_desc for 41 service pages
  2. site/build.py           — title/description args in write() calls for 8 core pages
  3. site/index.html         — hand-written home page (6 meta fields)
  4. site/<page>.html        — all 50 generated HTMLs (6 meta fields each)

Source of these values: SEO team's "DV - Meta optimization - Sheet1.pdf" (50 entries).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"

# --------------------------------------------------------------------------- #
# 50 entries from the SEO sheet: (filename, meta_title, meta_description)
# --------------------------------------------------------------------------- #
ENTRIES: list[tuple[str, str, str]] = [
    # Core pages (1–9)
    ("index.html",
     "Best Digital Marketing Agency in India | Digiveritaz",
     "Digiveritaz is a performance-driven digital marketing agency in India delivering SEO, PPC, branding and growth strategies for measurable business success."),
    ("about-us.html",
     "About Digiveritaz | Digital Marketing Agency India",
     "Learn about Digiveritaz, an India-based digital marketing agency helping brands grow through SEO, paid ads, branding, and ROI-focused strategies."),
    ("services.html",
     "Best Digital Marketing Services in India | Digiveritaz",
     "Explore Digiveritaz full-suite digital marketing services in India including SEO, PPC, performance marketing, paid social, WhatsApp marketing and branding."),
    ("case-study.html",
     "Case Studies | DigiVeritaz Digital Marketing Success Stories",
     "Explore real-world digital marketing case studies showcasing Digiveritaz growth-driven results for brands across India — lead gen, SEO and PPC wins included."),
    ("blog.html",
     "Digital Marketing Blogs and Insights | DigiVeritaz India",
     "Explore expert insights, trends and strategies on SEO, PPC, AI and performance marketing from Digiveritaz — updated weekly for brands and marketers in India."),
    ("contact-us.html",
     "Contact Digiveritaz | Digital Marketing Agency India",
     "Get in touch with Digiveritaz to discuss SEO, PPC and performance marketing solutions for your business in India. Book a free 30-min strategy call today."),
    ("faq.html",
     "Frequently Asked Questions (FAQ's) | Digiveritaz India",
     "Find answers to common questions about Digiveritaz digital marketing, SEO and performance marketing services for businesses and brands across all of India."),
    ("privacy-policy.html",
     "Privacy Policy | Digiveritaz Digital Marketing India",
     "Read Digiveritaz privacy policy to understand how we collect, use and protect your personal and business data responsibly across all operations in India."),
    ("terms-and-conditions.html",
     "Terms & Conditions | Digiveritaz Digital Marketing India",
     "Review the terms and conditions governing the use of Digiveritaz website, services and digital marketing solutions for businesses and brands across India."),

    # Marketing (10–19)
    ("seo.html",
     "SEO Services in India for Business Growth | Digiveritaz",
     "Boost rankings, traffic and leads with Digiveritaz data-led SEO services in India focused on long-term organic growth and measurable search performance."),
    ("social-media-management.html",
     "Social Media Management Services in India | Digiveritaz",
     "Manage and grow your brand presence with Digiveritaz social media management services in India — strategy, content creation and monthly performance reporting."),
    ("influencer-marketing.html",
     "Influencer Marketing Agency Services in India | Digiveritaz",
     "Boost brand reach with Digiveritaz influencer marketing services in India through creator partnerships, campaigns, audience engagement, and ROI-driven growth."),
    ("digital-pr.html",
     "Digital PR Marketing Agency Services in India | Digiveritaz",
     "Earn editorial coverage, high-DA backlinks and authoritative brand mentions across India top publications with Digiveritaz digital PR campaigns and outreach."),
    ("online-reputation-management.html",
     "Online Reputation Management Services in India | Digiveritaz",
     "Suppress negative content, monitor brand mentions and build a strong trusted online reputation for your business in India with Digiveritaz ORM services."),
    ("organic-marketing-services.html",
     "Content Marketing Agency Services in India | Digiveritaz",
     "Build lasting visibility with Digiveritaz content marketing services in India — blog strategy, pillar pages, topical clusters and editorial systems that rank."),
    ("whatsapp-marketing-services.html",
     "WhatsApp Marketing Agency Services in India | Digiveritaz",
     "Drive customer engagement and leads with Digiveritaz WhatsApp marketing services in India — broadcast sequences, chatbot automation and click-to-WhatsApp ads."),
    ("performance-marketing-agency.html",
     "Performance Marketing Agency services in India | Digiveritaz",
     "Drive measurable growth with Digiveritaz performance marketing strategies in India — full-funnel campaigns focused on CAC, ROAS and real revenue results."),
    ("ecommerce-marketing.html",
     "Ecommerce Marketing Agency Services in India | Digiveritaz",
     "Scale your online store with Digiveritaz ecommerce marketing services in India — Google Shopping, Meta Ads, SEO, email automation and marketplace growth."),
    ("generative-search-optimisation.html",
     "Generative Search Optimisation Services in India | Digiveritaz",
     "Optimize for AI-powered search with Digiveritaz Generative Search Optimisation strategies in India — get found in ChatGPT, Gemini and Google AI Overviews."),

    # Advertising (20–26)
    ("pay-per-click.html",
     "PPC Management Services Google Ads India | Digiveritaz",
     "Maximize ROI with Digiveritaz PPC management services in India across Google Ads and paid platforms — keyword strategy, ad copy and conversion tracking done."),
    ("display-advertising.html",
     "Display Advertising Services Agency India | Digiveritaz",
     "Reach your target audience with Digiveritaz display advertising services in India — GDN, programmatic, retargeting and native ad campaigns built for results."),
    ("facebook-instagram-advertising.html",
     "Facebook Instagram Advertising Agency India | Digiveritaz",
     "Scale reach and conversions with Digiveritaz Facebook and Instagram advertising services in India — Reels, Stories and Advantage+ campaigns built for ROAS."),
    ("shopping-ads.html",
     "Google Shopping Ads Management India | Digiveritaz",
     "Drive more e-commerce sales with Digiveritaz Google Shopping ads services in India — product feed optimisation, margin-first bidding and full ROAS tracking."),
    ("paid-social-media-advertising.html",
     "Paid Social Media Advertising Agency India | Digiveritaz",
     "Scale reach and conversions with Digiveritaz paid social media advertising in India across LinkedIn, X, TikTok and YouTube — full-funnel campaigns that work."),
    ("amazon-marketing.html",
     "Amazon Marketing Services Agency India | Digiveritaz",
     "Grow your Amazon brand with Digiveritaz Amazon marketing services in India — Sponsored Products, Sponsored Brands, Display Ads and A+ content optimisation."),
    ("native-advertising.html",
     "Native Advertising Services Agency India | Digiveritaz",
     "Reach audiences naturally with Digiveritaz native advertising solutions in India — premium publisher placements via Taboola and Outbrain that earn attention."),

    # Design & Content (27–31)
    ("ui-ux-design.html",
     "Conversion-Focused UI UX Design India | Digiveritaz",
     "Create intuitive, conversion-focused digital experiences with Digiveritaz UI UX design services in India — wireframes, prototypes and full design systems."),
    ("product-design.html",
     "Product Design Services Agency in India | Digiveritaz",
     "Build user-centred products with Digiveritaz product design services in India — discovery workshops, interaction design and launch-ready specs your team ships."),
    ("branding-and-design.html",
     "Branding & Design Services Agency in India | Digiveritaz",
     "Create impactful brand identities with Digiveritaz strategic branding and design solutions in India — logo, colour, typography and full brand guidelines built."),
    ("communication-design.html",
     "Communication Design Services Agency in India | Digiveritaz",
     "Communicate your brand clearly with Digiveritaz communication design services in India — pitch decks, brochures, social templates and sales collateral done."),
    ("content-copy-writing.html",
     "Copywriting Content Marketing Agency in India | Digiveritaz",
     "Drive action with Digiveritaz copywriting and content services in India — conversion copy, SEO articles, email sequences written by senior strategists only."),

    # Strategy & Data (32–42)
    ("conversion-rate-optimisation.html",
     "Conversion Rate Optimisation Services in India | Digiveritaz",
     "Increase conversions with Digiveritaz CRO services in India — experiment-led A/B testing, heuristic audits and data-backed changes that improve your results."),
    ("revenue-generation.html",
     "Revenue Generation Marketing Agency in India | Digiveritaz",
     "Accelerate business growth with Digiveritaz revenue generation services in India — full-funnel programmes built around CAC, LTV and cohort retention models."),
    ("lead-generation.html",
     "Lead Generation Services in India for B2B,B2C | Digiveritaz",
     "Generate qualified leads with Digiveritaz lead generation services in India — B2B and B2C lead engines with real attribution, lead scoring and MQL-to-SQL flows."),
    ("cmo-consultancy.html",
     "Fractional CMO Consultancy Services in India | Digiveritaz",
     "Scale your marketing with Digiveritaz fractional CMO services in India — strategic direction, OKRs, 90-day roadmaps and investor-ready growth narratives done."),
    ("landing-page-design.html",
     "Landing Page Design Services Agency in India | Digiveritaz",
     "Convert more visitors with Digiveritaz landing page design services in India — CRO-optimised copy, design and full conversion tracking delivered in 48 hours."),
    ("real-estate-lead-generation.html",
     "Real Estate Lead Generation Services in India | Digiveritaz",
     "Generate qualified property leads with Digiveritaz real estate lead generation services in India — RERA-compliant funnels for residential and resale projects."),
    ("research-and-insights.html",
     "Market Research & Insights Services in India | Digiveritaz",
     "Make smarter business decisions with Digiveritaz market research services in India — audience surveys, cohort analysis, competitor teardowns and modelling."),
    ("strategy-and-planning.html",
     "Marketing Strategy & Planning Agency in India | Digiveritaz",
     "Build a winning marketing roadmap with Digiveritaz strategy and planning services in India — quarterly horizon models your leadership team can execute on."),
    ("analytics-configuration.html",
     "GA4 Analytics Configuration Services in India | Digiveritaz",
     "Get clean, actionable data with Digiveritaz GA4 analytics configuration services in India — proper taxonomy, attribution and Looker Studio dashboards built."),
    ("google-tag-manager.html",
     "Google Tag Manager Services in India | Digiveritaz",
     "Implement clean, reliable tracking with Digiveritaz Google Tag Manager services in India — server-side tagging and consent-mode governance that holds up well."),
    ("data-strategy-consulting-services.html",
     "Data Strategy Consulting Services in India | Digiveritaz",
     "Turn data into decisions with Digiveritaz data strategy consulting services in India for smarter marketing measurement and business growth across all teams."),

    # Tech & Development (43–50)
    ("website-development.html",
     "Website Development Services Agency in India | Digiveritaz",
     "Build fast, conversion-focused websites with Digiveritaz website development services in India — custom design, SEO-ready architecture and mobile-first builds."),
    ("custom-software-development.html",
     "Custom Software Development Services in India | Digiveritaz",
     "Build scalable custom software with Digiveritaz development services in India — web apps, automation tools, API integrations and backend systems built right."),
    ("ecommerce-development.html",
     "Ecommerce Development Services in India | Digiveritaz",
     "Launch your online store with Digiveritaz ecommerce development services in India — Shopify, WooCommerce and headless commerce builds optimised for conversion."),
    ("wordpress-development.html",
     "WordPress Development Services in India | Digiveritaz",
     "Build and optimise WordPress websites with Digiveritaz in India — custom themes, plugin development, speed optimisation and complete SEO-ready architecture."),
    ("mobile-app-development.html",
     "Mobile App Development Services in India | Digiveritaz",
     "Build high-performance iOS and Android apps with Digiveritaz mobile app development services in India — UI/UX design, development and App Store launch support."),
    ("linux-hosting.html",
     "Linux Managed Hosting Services in India | Digiveritaz",
     "Host your business on secure Linux servers with Digiveritaz hosting services in India — managed infrastructure, guaranteed uptime and daily backups included."),
    ("business-email.html",
     "Business Email Hosting Services in India | Digiveritaz",
     "Set up professional business email with Digiveritaz in India — custom domain, spam protection, seamless migration support and complete admin management done."),
    ("crm-services.html",
     "CRM Setup Integration Services in India | Digiveritaz",
     "Streamline your sales pipeline with Digiveritaz CRM services in India — pipeline setup, automation workflows and marketing-to-sales data synchronisation done."),
]

CORE_PAGES = {  # build.py write("FILENAME", ...) calls (no service pages)
    "about-us.html", "contact-us.html", "services.html", "case-study.html",
    "blog.html", "faq.html", "privacy-policy.html", "terms-and-conditions.html",
}
SERVICE_PAGES = {fn for fn, _, _ in ENTRIES} - CORE_PAGES - {"index.html"}


def html_escape(text: str) -> str:
    """HTML-escape only & — site already uses &amp; throughout."""
    return text.replace("&", "&amp;")


# --------------------------------------------------------------------------- #
# 1. Update each generated HTML file (6 meta fields)
# --------------------------------------------------------------------------- #
def update_html(path: Path, title: str, desc: str) -> int:
    """Replace title + 5 meta fields. Returns number of substitutions made."""
    t = html_escape(title)
    d = html_escape(desc)
    src = path.read_text(encoding="utf-8")
    out, total = src, 0
    patterns = [
        (re.compile(r"<title>[^<]*</title>"),
         f"<title>{t}</title>"),
        (re.compile(r'<meta name="description" content="[^"]*">'),
         f'<meta name="description" content="{d}">'),
        (re.compile(r'<meta property="og:title" content="[^"]*">'),
         f'<meta property="og:title" content="{t}">'),
        (re.compile(r'<meta property="og:description" content="[^"]*">'),
         f'<meta property="og:description" content="{d}">'),
        (re.compile(r'<meta name="twitter:title" content="[^"]*">'),
         f'<meta name="twitter:title" content="{t}">'),
        (re.compile(r'<meta name="twitter:description" content="[^"]*">'),
         f'<meta name="twitter:description" content="{d}">'),
    ]
    for pat, repl in patterns:
        out, n = pat.subn(repl, out, count=1)
        total += n
    if total != 6:
        raise RuntimeError(f"{path.name}: expected 6 replacements, got {total}")
    if out != src:
        path.write_text(out, encoding="utf-8")
    return total


# --------------------------------------------------------------------------- #
# 2. Update services_data.py meta_title / meta_desc per service entry.
#    services_data.py is auto-generated from a docx, but it's the current
#    source-of-truth for build.py. Each entry is a dict; meta_desc may span
#    multiple lines via Python implicit string concatenation.
# --------------------------------------------------------------------------- #
def update_services_data(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out = list(lines)
    # Locate every site_slug line, then update meta_title / meta_desc that
    # follow it (within the same dict — bounded by next site_slug or EOF).
    slug_indices: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        m = re.match(r"\s*'site_slug':\s*'([^']+)'", line)
        if m:
            slug_indices.append((i, m.group(1)))
    slug_indices.append((len(lines), ""))  # sentinel

    updated_for: dict[str, tuple[str, str]] = {
        fn: (title, desc) for fn, title, desc in ENTRIES if fn in SERVICE_PAGES
    }

    updated = 0
    # Process in REVERSE so that mutating out[start:end] (whose length may
    # change when a multi-line meta_desc collapses) doesn't shift the
    # original indices we still need for earlier entries.
    pairs = list(zip(slug_indices, slug_indices[1:]))
    for (start, slug), (end, _) in reversed(pairs):
        if slug not in updated_for:
            continue
        title, desc = updated_for[slug]
        # Escape single quotes for Python string literal
        title_py = title.replace("\\", "\\\\").replace("'", "\\'")
        desc_py = desc.replace("\\", "\\\\").replace("'", "\\'")

        # Find meta_title line (single-line) and meta_desc block (1+ lines).
        # Values may use either single or double quotes (Python auto-switches
        # to double quotes if the string contains a single quote).
        block = lines[start:end]
        new_block = []
        i = 0
        replaced_title = replaced_desc = False
        # Matches a complete single-line string value, either '...' or "..."
        title_re = re.compile(
            r"""(\s*)'meta_title':\s*"""
            r"""(?:'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")"""
            r"""\s*,\s*$"""
        )
        desc_open_re = re.compile(r"""(\s*)'meta_desc':\s*['"]""")
        # End-of-block marker: line ends with `',` or `",` (the value's closing
        # quote followed by a comma).
        desc_close_re = re.compile(r"""['"]\s*,\s*$""")
        while i < len(block):
            ln = block[i]
            m_t = title_re.match(ln)
            if m_t and not replaced_title:
                indent = m_t.group(1)
                new_block.append(f"{indent}'meta_title': '{title_py}',\n")
                replaced_title = True
                i += 1
                continue
            m_d = desc_open_re.match(ln)
            if m_d and not replaced_desc:
                indent = m_d.group(1)
                # Skip continuation lines until line that ends with `',` or `",`
                while i < len(block) and not desc_close_re.search(block[i]):
                    i += 1
                if i < len(block):
                    i += 1  # consume the closing line itself
                new_block.append(f"{indent}'meta_desc': '{desc_py}',\n")
                replaced_desc = True
                continue
            new_block.append(ln)
            i += 1

        if not (replaced_title and replaced_desc):
            raise RuntimeError(
                f"services_data.py: failed to update {slug} "
                f"(title={replaced_title}, desc={replaced_desc})"
            )
        out[start:end] = new_block
        updated += 1

    path.write_text("".join(out), encoding="utf-8")
    return updated


# --------------------------------------------------------------------------- #
# 3. Update build.py write("FILENAME", "<title>", "<desc>", ...) calls
#    for the 8 core pages.
# --------------------------------------------------------------------------- #
def update_build_py(path: Path) -> int:
    src = path.read_text(encoding="utf-8")
    out = src
    updated = 0
    for fn, title, desc in ENTRIES:
        if fn not in CORE_PAGES:
            continue
        t = html_escape(title).replace('"', '\\"')
        d = html_escape(desc).replace('"', '\\"')
        # Match: write("filename.html",\n      "<old title>",\n      "<old desc>",
        pattern = re.compile(
            r'(write\("' + re.escape(fn) + r'",\s*\n\s*")[^"]*("\s*,\s*\n\s*")[^"]*(",)',
            re.MULTILINE,
        )
        new, n = pattern.subn(rf'\g<1>{t}\g<2>{d}\g<3>', out, count=1)
        if n != 1:
            raise RuntimeError(f"build.py: failed to update write() for {fn} (matches={n})")
        out = new
        updated += 1
    path.write_text(out, encoding="utf-8")
    return updated


def main() -> int:
    print(f"Site root: {SITE}")
    if not SITE.is_dir():
        print(f"ERROR: site directory not found at {SITE}", file=sys.stderr)
        return 1

    # --- 1. HTML files -----------------------------------------------------
    print("\n[1/3] Updating generated HTML files…")
    html_count = 0
    missing: list[str] = []
    for fn, title, desc in ENTRIES:
        p = SITE / fn
        if not p.is_file():
            missing.append(fn)
            continue
        update_html(p, title, desc)
        html_count += 1
        print(f"  ✓ {fn}")
    if missing:
        print(f"\nERROR: missing HTML files: {missing}", file=sys.stderr)
        return 1

    # --- 2. services_data.py ----------------------------------------------
    print("\n[2/3] Updating services_data.py…")
    svc_count = update_services_data(SITE / "services_data.py")
    print(f"  ✓ {svc_count} service entries updated")

    # --- 3. build.py -------------------------------------------------------
    print("\n[3/3] Updating build.py (core pages)…")
    core_count = update_build_py(SITE / "build.py")
    print(f"  ✓ {core_count} core-page write() calls updated")

    print(
        f"\nDone. HTML files: {html_count} | services_data.py entries: {svc_count} "
        f"| build.py core pages: {core_count}"
    )
    expected_services = len(SERVICE_PAGES)
    expected_core = len(CORE_PAGES)
    if svc_count != expected_services or core_count != expected_core:
        print(
            f"WARNING: counts mismatch — expected {expected_services} services / "
            f"{expected_core} core pages",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
