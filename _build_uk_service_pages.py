#!/usr/bin/env python3
"""
Build UK versions of the top-5 service pages.

For each India source page, this script:
  1. Reads site/<slug>.html
  2. Applies a deterministic set of head + body transformations to localize it for the UK
  3. Writes site/uk/<slug>.html
  4. Reports any remaining "India"/"Mumbai"/"rupee"/"₹" hits in the body for manual review

Run from repo root: python3 _build_uk_service_pages.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent / "site"
UK_DIR = ROOT / "uk"
UK_DIR.mkdir(exist_ok=True)

# Per-service UK-targeted metadata
SERVICES = {
    "seo": {
        "title":    "Best SEO Agency in the UK — Rankings, Traffic & Leads | DigiVeritaz",
        "desc":     "DigiVeritaz delivers data-led SEO services in the UK — technical SEO, content strategy and local SEO that grow rankings, traffic and qualified leads.",
        "keywords": "seo agency uk, seo services uk, best seo agency uk, seo company london, technical seo uk, ecommerce seo uk, local seo london, b2b seo uk, organic seo agency uk, seo consultant london",
    },
    "pay-per-click": {
        "title":    "PPC Agency in the UK — Google & Bing Ads Management | DigiVeritaz",
        "desc":     "DigiVeritaz manages high-ROI PPC campaigns in the UK across Google Ads and Bing — keyword, bidding and landing-page optimisation for measurable leads.",
        "keywords": "ppc agency uk, ppc services uk, google ads agency uk, google ads management london, bing ads uk, ppc consultant london, paid search uk, performance ppc uk, b2b ppc uk",
    },
    "performance-marketing-agency": {
        "title":    "Performance Marketing Agency in the UK — ROI-First Campaigns | DigiVeritaz",
        "desc":     "DigiVeritaz is a UK performance marketing agency running ROI-obsessed search, shopping, video and social campaigns with full-funnel attribution.",
        "keywords": "performance marketing agency uk, roi marketing agency uk, full funnel marketing london, attribution agency uk, growth marketing uk, b2b performance marketing uk",
    },
    "paid-social-media-advertising": {
        "title":    "Paid Social Advertising in the UK — Meta, TikTok & LinkedIn Ads | DigiVeritaz",
        "desc":     "DigiVeritaz runs paid social campaigns for UK brands across Meta, TikTok and LinkedIn Ads — creative-led, CRO-tested funnels that drive ROAS.",
        "keywords": "paid social agency uk, meta ads agency uk, tiktok ads agency uk, linkedin ads agency uk, facebook ads management london, instagram ads agency uk, b2b linkedin ads uk",
    },
    "generative-search-optimisation": {
        "title":    "GEO Agency in the UK — Generative Engine Optimisation | DigiVeritaz",
        "desc":     "DigiVeritaz is a UK Generative Engine Optimisation (GEO) agency helping brands rank in ChatGPT, Perplexity, Gemini and Google AI Overviews.",
        "keywords": "geo agency uk, generative engine optimisation uk, ai search optimisation uk, chatgpt seo uk, perplexity optimisation uk, gemini optimisation uk, ai seo agency london",
    },
}

# Body-level localisation swaps (apply to every UK service page).
# Conservative: only swap phrases that almost certainly leak India to UK visitors.
BODY_SWAPS = [
    # Currency / Indian units
    (re.compile(r"₹"),                  "£"),
    (re.compile(r"\bLakh\b"),           "K"),
    (re.compile(r"\bLakhs\b"),          "K"),
    (re.compile(r"\brupees?\b"),        "pounds"),
    (re.compile(r"\bRupees?\b"),        "Pounds"),
    # India market framing
    (re.compile(r"\bin India\b"),                  "in the UK"),
    (re.compile(r"\bIn India\b"),                  "In the UK"),
    (re.compile(r"\bacross India\b"),              "across the UK"),
    (re.compile(r"\bAcross India\b"),              "Across the UK"),
    (re.compile(r"\bbrands across India\b"),       "brands across the UK"),
    (re.compile(r"\bMumbai-based\b"),              "UK-focused"),
    (re.compile(r"\bMumbai based\b"),              "UK focused"),
    (re.compile(r"\bpan-India\b"),                 "multi-market"),
    (re.compile(r"\bpan India\b"),                 "multi-market"),
    (re.compile(r"\bHyundai India\b"),             "Hyundai"),

    # Service eyebrow tags: "· Mumbai" → "· UK"
    (re.compile(r"· Mumbai</span>"),                                 "· UK</span>"),

    # Fake browser/AI screenshot examples on the page (visual proof artefacts)
    (re.compile(r"Google Search · India · live"),                    "Google Search · UK · live"),
    (re.compile(r"Google Ad · live for &quot;SEO agency Mumbai&quot;"), "Google Ad · live for &quot;SEO agency London&quot;"),
    (re.compile(r'Google Ad · live for "SEO agency Mumbai"'),        'Google Ad · live for "SEO agency London"'),
    (re.compile(r"best digital marketing agencies in Mumbai"),        "best digital marketing agencies in London"),
    (re.compile(r"SEO agency Mumbai pricing"),                       "SEO agency London pricing"),
    (re.compile(r"digital PR agency India"),                         "digital PR agency UK"),
    (re.compile(r"B2B Lead Gen · India audience"),                   "B2B Lead Gen · UK audience"),

    # H2/H3 "Agency in Mumbai" patterns (NOT "Mumbai HQ" — that's the real office)
    (re.compile(r"\bSEO Agency in Mumbai\b"),                        "SEO Agency in London"),
    (re.compile(r"\bPPC Agency in Mumbai\b"),                        "PPC Agency in London"),
    (re.compile(r"\bSocial Media Advertising Agency in Mumbai\b"),   "Social Media Advertising Agency in London"),
    (re.compile(r"\bsocial media advertising agency in Mumbai\b"),   "social media advertising agency in London"),
    (re.compile(r"\bGoogle Partner PPC agency in Mumbai\b"),         "Google Partner PPC agency in London"),
    (re.compile(r"\bagency in Mumbai\b"),                            "agency in London"),
    (re.compile(r"\bagencies in Mumbai\b"),                          "agencies in London"),

    # Generic "Mumbai" body mentions — use negative lookahead to preserve "Mumbai HQ" + Mumbai street address
    (re.compile(r"\btop-rated SEO agency in Mumbai\b"),              "top-rated SEO agency in London"),
    (re.compile(r"\bSEO agency in Mumbai\b"),                        "SEO agency in London"),
    (re.compile(r"\bagency in Mumbai\b"),                            "agency in London"),
    (re.compile(r"\bMumbai &amp; India\b"),                          "London &amp; UK"),
    (re.compile(r"\bMumbai and India\b"),                            "London and the UK"),
    (re.compile(r"\bgeo-targeted landing pages for Mumbai\b"),       "geo-targeted landing pages for UK cities"),

    # Indian search landscape framing
    (re.compile(r"\bIndian search landscape\b"),                     "UK search landscape"),

    # Brand SEO copy
    (re.compile(r"top-rated SEO agency in Mumbai &amp; India"),      "top-rated SEO agency in London &amp; the UK"),

    # Multi-city references (Andheri/Bandra/Navi Mumbai/Pune are Mumbai areas — replace with UK cities)
    (re.compile(r"Andheri, Bandra, Navi Mumbai, Pune"),              "London, Manchester, Birmingham, Leeds"),

    # Trailing partial-swap cleanup: "London & India" → "London & the UK"
    (re.compile(r"\bin London &amp; India\b"),                       "in London &amp; the UK"),
    (re.compile(r"\bLondon &amp; India\b"),                          "London &amp; the UK"),
    (re.compile(r"\bagency in London &amp; India\b"),                "agency in London &amp; the UK"),

    # Fake search keyword examples
    (re.compile(r"&quot;best SEO agency India&quot;"),               "&quot;best SEO agency UK&quot;"),
    (re.compile(r'"best SEO agency India"'),                         '"best SEO agency UK"'),
    (re.compile(r"SEO services India"),                              "SEO services UK"),
    (re.compile(r"&quot;SEO services India&quot;"),                  "&quot;SEO services UK&quot;"),
    (re.compile(r'"SEO services India"'),                            '"SEO services UK"'),

    # Indian publications → UK publications
    (re.compile(r"\bcredible Indian and international publications\b"), "credible UK and international publications"),
    (re.compile(r"\bIndian and international\b"),                    "UK and international"),

    # JSON-LD schema localisation
    (re.compile(r'"areaServed":\{"@type":"Country","name":"India"\}'), '"areaServed":{"@type":"Country","name":"United Kingdom"}'),
    (re.compile(r'"priceCurrency":"INR"'),                           '"priceCurrency":"GBP"'),

    # Indian Rupee prices in schema/text (₹35,000 → £350 rough conversion; pricing should be reviewed by business)
    (re.compile(r"₹35,000"),                                         "£350"),
    (re.compile(r"₹50,000"),                                         "£500"),
    (re.compile(r"₹1,00,000"),                                       "£1,000"),
    (re.compile(r"₹2,00,000"),                                       "£2,000"),
    (re.compile(r"₹35,000"),                                    "£350"),
    (re.compile(r"₹50,000"),                                    "£500"),

    # JSON-LD doesn't use HTML entities — handle plain ampersand "London & India" / "Mumbai & India" / similar
    (re.compile(r"\bLondon & India\b"),                              "London & the UK"),
    (re.compile(r"\bMumbai & India\b"),                              "London & the UK"),
    (re.compile(r"\bSEO agency in London & India\b"),                "SEO agency in London & the UK"),
    (re.compile(r"\btop-rated SEO agency in London & India\b"),      "top-rated SEO agency in London & the UK"),

    # JSON-encoded rupee codepoint (₹ literal 6 chars in source)
    (re.compile(r"\\u20b935,000"),                                   "£350"),
    (re.compile(r"\\u20b950,000"),                                   "£500"),
    (re.compile(r"approximately \\u20b9([\d,]+) per month"),         r"approximately £\1 per month"),
    (re.compile(r"\\u20b9"),                                         "£"),

    # Schema/breadcrumb "Services India" → "Services UK" (page title patterns)
    (re.compile(r"\bServices India\b"),                              "Services UK"),
    (re.compile(r"\(GEO\) Services India"),                          "(GEO) Services UK"),
    (re.compile(r"\bIndia's first GEO agency\b"),                    "the UK's leading GEO agency"),
    (re.compile(r"\bIndia's first\b"),                                "the UK's leading"),

    # "Indian businesses/brands/companies" → "UK businesses/brands/companies"
    (re.compile(r"\bIndian businesses\b"),                            "UK businesses"),
    (re.compile(r"\bIndian brands\b"),                                "UK brands"),
    (re.compile(r"\bIndian companies\b"),                             "UK companies"),
    (re.compile(r"\bIndian market\b"),                                "UK market"),
    (re.compile(r"\bin the Indian market\b"),                         "in the UK market"),

    # Generic "for India" / "across India" misses
    (re.compile(r"\bfor India\b"),                                    "for the UK"),
    (re.compile(r"\bIn India,\b"),                                    "In the UK,"),

    # "Mumbai" generic positioning misses (preserves "Mumbai HQ", "Mumbai 400088", "Mumbai, Maharashtra")
    (re.compile(r"\bMumbai-built\b"),                                 "UK-focused"),
    (re.compile(r"\bMumbai businesses\b"),                            "UK businesses"),
    (re.compile(r"\bMumbai brands\b"),                                "UK brands"),
    (re.compile(r"\bMumbai companies\b"),                             "UK companies"),
    (re.compile(r"\bMumbai market\b"),                                "UK market"),
    (re.compile(r"\bMumbai retail\b"),                                "UK retail"),
    (re.compile(r"\bMumbai e-commerce\b"),                            "UK e-commerce"),
    (re.compile(r"\bMumbai property\b"),                              "UK property"),
    (re.compile(r"\bMumbai real estate\b"),                           "UK real estate"),
    (re.compile(r"\bMumbai-based brands\b"),                          "UK brands"),
    (re.compile(r"\bMumbai SMBs\b"),                                  "UK SMBs"),

    # Schema "Agency Mumbai" / "Agency India" name patterns (no preposition)
    (re.compile(r"\bPPC Agency Mumbai\b"),                            "PPC Agency London"),
    (re.compile(r"\bSEO Agency Mumbai\b"),                            "SEO Agency London"),
    (re.compile(r"\bPerformance Marketing Agency India\b"),           "Performance Marketing Agency UK"),
    (re.compile(r"\bPerformance Marketing Agency Mumbai\b"),          "Performance Marketing Agency London"),
    (re.compile(r"\bSocial Media Advertising Agency Mumbai\b"),       "Social Media Advertising Agency London"),
    (re.compile(r"\bPaid Social Agency Mumbai\b"),                    "Paid Social Agency London"),
    (re.compile(r"\bDigital Marketing Agency Mumbai\b"),              "Digital Marketing Agency London"),
    (re.compile(r"\bDigital Marketing Agency India\b"),               "Digital Marketing Agency UK"),

    # H2/H3 patterns "for Indian Brands" / "for Indian Businesses"
    (re.compile(r"\bfor Indian Brands\b"),                            "for UK Brands"),
    (re.compile(r"\bfor Indian Businesses\b"),                        "for UK Businesses"),
    (re.compile(r"\bfor Indian Companies\b"),                         "for UK Companies"),
    (re.compile(r"\bIndian Brands\b"),                                "UK Brands"),
]


# JSON-LD URL rewrites — schema breadcrumbs, Service URL, og:url not caught by head transform.
# Applied after BODY_SWAPS, per slug.
def transform_schema_urls(html: str, slug: str) -> str:
    # Breadcrumb position 2 + Service URL: "https://www.digiveritaz.com/<slug>/" → /uk/<slug>/
    # NOT the position 1 "Home" item (= root) which stays at /.
    for pattern in [
        f'"item":"https://www.digiveritaz.com/{slug}/"',
        f'"url":"https://www.digiveritaz.com/{slug}/"',
    ]:
        replacement = pattern.replace(f"/{slug}/", f"/uk/{slug}/")
        html = html.replace(pattern, replacement)
    return html

def transform_head(html: str, slug: str, meta: dict) -> str:
    """Apply head transformations: lang, title, meta description/keywords, canonical, hreflang, OG, Twitter."""

    # <html lang="en-IN"> → en-GB
    html = re.sub(r'<html lang="en-IN">', '<html lang="en-GB">', html, count=1)

    # <title>...</title>
    html = re.sub(r'<title>[^<]*</title>',
                  f'<title>{meta["title"]}</title>', html, count=1)

    # <meta name="description" content="...">
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{meta["desc"]}">',
        html, count=1
    )

    # <meta name="keywords" content="...">
    html = re.sub(
        r'<meta name="keywords" content="[^"]*">',
        f'<meta name="keywords" content="{meta["keywords"]}">',
        html, count=1
    )

    # Canonical /<slug>/ → /uk/<slug>/
    html = html.replace(
        f'<link rel="canonical" href="https://www.digiveritaz.com/{slug}/">',
        f'<link rel="canonical" href="https://www.digiveritaz.com/uk/{slug}/">'
    )

    # Replace en-IN / x-default hreflang block with the en-GB + en-IN + x-default trio.
    # Source has 2 lines: en-IN self + x-default self. Replace with UK-style trio.
    old_hreflang = (
        f'<link rel="alternate" hreflang="en-IN" href="https://www.digiveritaz.com/{slug}/">\n'
        f'<link rel="alternate" hreflang="x-default" href="https://www.digiveritaz.com/{slug}/">'
    )
    new_hreflang = (
        f'<link rel="alternate" hreflang="en-GB" href="https://www.digiveritaz.com/uk/{slug}/">\n'
        f'<link rel="alternate" hreflang="en-IN" href="https://www.digiveritaz.com/{slug}/">\n'
        f'<link rel="alternate" hreflang="x-default" href="https://www.digiveritaz.com/">'
    )
    html = html.replace(old_hreflang, new_hreflang)

    # OG title + description + URL + locale
    html = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{meta["title"]}">',
        html, count=1
    )
    html = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{meta["desc"]}">',
        html, count=1
    )
    html = html.replace(
        f'<meta property="og:url" content="https://www.digiveritaz.com/{slug}/">',
        f'<meta property="og:url" content="https://www.digiveritaz.com/uk/{slug}/">'
    )
    html = html.replace(
        '<meta property="og:locale" content="en_IN">',
        '<meta property="og:locale" content="en_GB">'
    )

    # Twitter title + description
    html = re.sub(
        r'<meta name="twitter:title" content="[^"]*">',
        f'<meta name="twitter:title" content="{meta["title"]}">',
        html, count=1
    )
    html = re.sub(
        r'<meta name="twitter:description" content="[^"]*">',
        f'<meta name="twitter:description" content="{meta["desc"]}">',
        html, count=1
    )

    return html


def transform_body(html: str) -> tuple[str, int]:
    """Apply body-level localisation swaps. Returns (new_html, num_swaps)."""
    swap_count = 0
    for pattern, replacement in BODY_SWAPS:
        new_html, n = pattern.subn(replacement, html)
        swap_count += n
        html = new_html
    return html, swap_count


def find_residual_india_hits(html: str) -> list[str]:
    """Find lines that still contain India/Mumbai/rupee/₹ for manual review.
    Excludes lines that are clearly correct (schema HQ address, hreflang en-IN link, etc.)."""
    hits = []
    for i, line in enumerate(html.split("\n"), 1):
        if re.search(r"\b(India|Mumbai|rupee|Rupee)\b|₹", line):
            # Skip lines that are legitimately India-referencing (schema address, hreflang to India)
            if any(skip in line for skip in [
                "hreflang=\"en-IN\"",
                "addressLocality",
                "addressRegion",
                "streetAddress",
                "postalCode",
                "Indian Rup",  # currency code in schema if any
                "@en-IN",
            ]):
                continue
            hits.append(f"  L{i}: {line.strip()[:120]}")
    return hits


def main():
    print("=" * 70)
    print("Building UK service pages")
    print("=" * 70)

    for slug, meta in SERVICES.items():
        src = ROOT / f"{slug}.html"
        dst = UK_DIR / f"{slug}.html"

        if not src.exists():
            print(f"❌ MISSING source: {src}")
            continue

        html = src.read_text(encoding="utf-8")
        html = transform_head(html, slug, meta)
        html, body_swaps = transform_body(html)
        html = transform_schema_urls(html, slug)

        dst.write_text(html, encoding="utf-8")
        residual = find_residual_india_hits(html)

        print(f"\n📄 {slug}.html → uk/{slug}.html")
        print(f"   Body swaps applied: {body_swaps}")
        print(f"   Residual India/Mumbai/₹ hits needing review: {len(residual)}")
        if residual and len(residual) <= 20:
            for hit in residual:
                print(hit)
        elif residual:
            for hit in residual[:10]:
                print(hit)
            print(f"   ... and {len(residual) - 10} more")

    print("\n" + "=" * 70)
    print("Done. Now run hreflang back-link and sitemap updates separately.")


if __name__ == "__main__":
    main()
