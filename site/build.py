#!/usr/bin/env python3
"""Static page builder for DigiVeritaz recreation.
Generates all HTML pages from shared header/footer + per-page content blocks.
"""
import os, pathlib, re as _pre_re

OUT = pathlib.Path(__file__).parent

NAV_ITEMS = [
    ("index.html", "Home", "nav.home"),
    ("about-us.html", "About Us", "nav.about"),
    ("services.html", "Services", "nav.services"),
    ("case-study.html", "Case Study", "nav.cases"),
    ("blog.html", "Blog", "nav.blog"),
    ("contact-us.html", "Contact Us", "nav.contact"),
]

THEME_TOGGLE = """      <li><button class="theme-toggle" aria-label="Toggle theme" title="Toggle theme">
        <svg class="icon-moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        <svg class="icon-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button></li>
"""

# Doc-driven service data (41 services, grouped categories, card metadata)
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from services_data import SERVICES as DOC_SERVICES, CATEGORIES as SVC_CATEGORIES, CARD_META as SVC_CARD_META

SERVICE_TITLE_MAP = {
    "seo.html": "SEO",
    "social-media-management.html": "Social Media Management",
    "influencer-marketing.html": "Influencer Marketing",
    "digital-pr.html": "Digital PR",
    "online-reputation-management.html": "Online Reputation Management",
    "organic-marketing-services.html": "Content Marketing",
    "whatsapp-marketing-services.html": "WhatsApp Marketing",
    "performance-marketing-agency.html": "Performance Marketing",
    "ecommerce-marketing.html": "E-Commerce Marketing",
    "generative-search-optimisation.html": "Generative Engine Optimisation",
    "pay-per-click.html": "Search PPC",
    "display-advertising.html": "Display Advertising",
    "facebook-instagram-advertising.html": "Facebook &amp; Instagram Ads",
    "shopping-ads.html": "Shopping Ads",
    "paid-social-media-advertising.html": "Social Media Advertising",
    "amazon-marketing.html": "Amazon Marketing",
    "native-advertising.html": "Native Advertising",
    "ui-ux-design.html": "UI/UX Design",
    "product-design.html": "Product Design",
    "branding-and-design.html": "Brand Identity",
    "communication-design.html": "Communication Design",
    "content-copy-writing.html": "Content &amp; Copywriting",
    "conversion-rate-optimisation.html": "Conversion Rate Optimisation",
    "revenue-generation.html": "Revenue Generation",
    "lead-generation.html": "Lead Generation",
    "cmo-consultancy.html": "CMO Consultancy",
    "landing-page-design.html": "Landing Page Design",
    "real-estate-lead-generation.html": "Real Estate Lead Generation",
    "research-and-insights.html": "Research &amp; Insights",
    "strategy-and-planning.html": "Strategy &amp; Planning",
    "analytics-configuration.html": "Analytics Configuration",
    "google-tag-manager.html": "Google Tag Manager",
    "data-strategy-consulting-services.html": "Data Strategy",
    "website-development.html": "Website Development",
    "custom-software-development.html": "Custom Software",
    "ecommerce-development.html": "E-Commerce Development",
    "wordpress-development.html": "WordPress Development",
    "mobile-app-development.html": "Mobile App Development",
    "linux-hosting.html": "Linux Hosting",
    "business-email.html": "Business Email",
    "crm-services.html": "CRM Services",
}

SERVICE_SLUGS = set(SERVICE_TITLE_MAP.keys()) | {"services.html"}

def build_nav(current):
    def is_active(href):
        if href == current: return True
        if href == "services.html" and current in SERVICE_SLUGS:
            return True
        if href == "blog.html" and current.startswith("blog-"):
            return True
        if href == "case-study.html" and current.startswith("case-study-"):
            return True
        return False

    def dropdown_html():
        cols = []
        for cat, slugs in SVC_CATEGORIES:
            items = "".join(
                f'<a href="{slug}" role="menuitem"{" class=\"active\"" if slug == current else ""}>{SERVICE_TITLE_MAP.get(slug, slug)}</a>'
                for slug in slugs
            )
            cols.append(f'<div class="mm-col"><div class="mm-head">{cat}</div>{items}</div>')
        view_all = f'<a class="mm-all" href="services.html"{" data-active=\"1\"" if current == "services.html" else ""}>View all services →</a>'
        return (
            '<div class="dd-menu mega-menu" role="menu">'
            '<span class="dd-bridge" aria-hidden="true"></span>'
            '<div class="mm-grid">' + "".join(cols) + '</div>'
            f'<div class="mm-foot">{view_all}</div>'
            '</div>'
        )

    lis_parts = []
    for h, t, k in NAV_ITEMS:
        active_cls = " active" if is_active(h) else ""
        if h == "services.html":
            lis_parts.append(
                f'<li class="has-dd has-mega"><a class="navlink{active_cls}" href="{h}" data-i18n="{k}">{t} <span class="dd-caret" aria-hidden="true">▾</span></a>{dropdown_html()}</li>'
            )
        else:
            lis_parts.append(
                f'<li><a class="navlink{active_cls}" href="{h}" data-i18n="{k}">{t}</a></li>'
            )
    lis = "\n      ".join(lis_parts)
    return f"""    <ul>
      {lis}
{THEME_TOGGLE}      <li class="cta"><a class="btn" href="contact-us.html" data-i18n="nav.cta">Book A Call</a></li>
    </ul>"""

SITE_URL = "https://digiveritaz.com"
DEFAULT_OG_IMAGE = "assets/logo.jpg"

ORG_SCHEMA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": ["Organization","LocalBusiness","ProfessionalService"],
            "@id": SITE_URL + "/#organization",
            "name": "DigiVeritaz",
            "alternateName": "DigiVeritaz Digital Marketing Agency",
            "url": SITE_URL,
            "logo": DEFAULT_OG_IMAGE,
            "image": DEFAULT_OG_IMAGE,
            "description": "DigiVeritaz is a Mumbai-based digital marketing agency delivering SEO, PPC, performance marketing, paid social, e-commerce growth, WhatsApp marketing, branding and data strategy services across India and worldwide.",
            "telephone": "+91-9956655662",
            "email": "durvamukherjee@digiveritaz.com",
            "priceRange": "$$",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "1st Floor, Ujagar Chambers, Bus Depot, Sion-Trombay Rd, opp. Deonar, Deonar, Chembur",
                "addressLocality": "Mumbai",
                "addressRegion": "Maharashtra",
                "postalCode": "400088",
                "addressCountry": "IN"
            },
            "geo": {"@type":"GeoCoordinates","latitude":19.0432,"longitude":72.9086},
            "areaServed": ["IN","US","AE","GB","SG","AU","CA"],
            "sameAs": [
                "https://www.facebook.com/digiveritaz",
                "https://www.instagram.com/digiveritaz",
                "https://www.linkedin.com/company/digiveritaz",
                "https://twitter.com/digiveritaz"
            ],
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.9",
                "reviewCount": "600",
                "bestRating": "5",
                "worstRating": "1"
            }
        },
        {
            "@type": "WebSite",
            "@id": SITE_URL + "/#website",
            "url": SITE_URL,
            "name": "DigiVeritaz",
            "publisher": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-IN"
        }
    ]
}

import json
ORG_JSONLD = json.dumps(ORG_SCHEMA, separators=(",",":"))
ORG_JSONLD_ESC = ORG_JSONLD.replace("{","{{").replace("}","}}")

HEAD_TPL = """<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta name="author" content="DigiVeritaz">
<meta name="publisher" content="DigiVeritaz">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<meta name="googlebot" content="index,follow">
<meta name="theme-color" content="#22c55e">
<meta name="format-detection" content="telephone=no">
<link rel="canonical" href="https://digiveritaz.com/{canonical}">
<link rel="alternate" hreflang="en-IN" href="https://digiveritaz.com/{canonical}">
<link rel="alternate" hreflang="x-default" href="https://digiveritaz.com/{canonical}">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="DigiVeritaz">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://digiveritaz.com/{canonical}">
<meta property="og:image" content="https://digiveritaz.com/assets/logo.jpg">
<meta property="og:image:alt" content="DigiVeritaz — Digital Marketing Agency">
<meta property="og:locale" content="en_IN">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@digiveritaz">
<meta name="twitter:creator" content="@digiveritaz">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://digiveritaz.com/assets/logo.jpg">

<!-- Favicon -->
<link rel="icon" type="image/png" href="assets/favicondv.png">
<link rel="apple-touch-icon" href="assets/favicondv.png">

<!-- Performance hints -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://digiveritaz.com" crossorigin>
<link rel="dns-prefetch" href="https://cdn.simpleicons.org">

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v={css_ver}">

<!-- Organization + Website schema -->
<script type="application/ld+json">""" + ORG_JSONLD_ESC + """</script>
{extra_jsonld}
<script>(function(){{var t=localStorage.getItem('dv-theme');if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}})();</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header" role="banner">
  <div class="container nav">
    <a class="brand" href="index.html">
      <img src="assets/logo.jpg" alt="DigiVeritaz">
      <span class="wordmark"><b>Digi</b>Veritaz</span>
    </a>
    <button class="hamb" aria-label="Menu">&#9776;</button>
    <nav aria-label="Primary" role="navigation">
{nav}
    </nav>
  </div>
</header>
"""

FOOT = """<footer class="site-footer" role="contentinfo">
  <div class="container">

    <div class="foot-main">
      <div class="footer-grid">

        <div>
          <a class="foot-brand" href="index.html">
            <img src="assets/logo.jpg" alt="DigiVeritaz">
            <span class="wordmark"><b>Digi</b>Veritaz</span>
          </a>
          <p class="foot-tag">DigiVeritaz is a Mumbai-based digital marketing agency helping brands across India achieve measurable ROI through SEO, Paid Media, Performance Marketing <strong>and MORE</strong>.</p>
          <div class="foot-socials">
            <a href="https://www.facebook.com/digiveritaz" aria-label="Facebook" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H8v-3h2.4V9.4c0-2.4 1.4-3.7 3.6-3.7 1 0 2.1.2 2.1.2v2.3h-1.2c-1.2 0-1.5.7-1.5 1.5V12h2.6l-.4 3h-2.2v7A10 10 0 0 0 22 12z"/></svg></a>
            <a href="https://www.instagram.com/digiveritaz" aria-label="Instagram" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.3 2.2.4.6.2 1 .5 1.5 1s.8.9 1 1.5c.1.4.3 1 .4 2.2.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.3 1.8-.4 2.2-.2.6-.5 1-1 1.5s-.9.8-1.5 1c-.4.1-1 .3-2.2.4-1.2.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.3-2.2-.4-.6-.2-1-.5-1.5-1s-.8-.9-1-1.5c-.1-.4-.3-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.3-1.8.4-2.2.2-.6.5-1 1-1.5s.9-.8 1.5-1c.4-.1 1-.3 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 8.1a3.2 3.2 0 1 0 0 6.4 3.2 3.2 0 0 0 0-6.4zm6.3-8.3a1.1 1.1 0 1 1-2.3 0 1.1 1.1 0 0 1 2.3 0z"/></svg></a>
            <a href="https://www.linkedin.com/company/digiveritaz" aria-label="LinkedIn" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2zM8 19H5V9h3v10zM6.5 7.7a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4zM19 19h-3v-5.3c0-1.3 0-2.9-1.8-2.9s-2 1.4-2 2.8V19h-3V9h2.9v1.4h0a3.2 3.2 0 0 1 2.9-1.6c3.1 0 3.7 2 3.7 4.7V19z"/></svg></a>
            <a href="https://twitter.com/digiveritaz" aria-label="X / Twitter" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M18.9 2H22l-7.5 8.6L23.5 22h-6.9l-5.4-7-6.2 7H2l8-9.2L1.7 2h7l4.9 6.5z"/></svg></a>
          </div>
        </div>

        <div>
          <h4>Services</h4>
          <ul>
            <li><a href="seo.html">SEO</a></li>
            <li><a href="pay-per-click.html">Pay Per Click</a></li>
            <li><a href="performance-marketing-agency.html">Performance Marketing</a></li>
            <li><a href="ecommerce-marketing.html">E-Commerce</a></li>
            <li><a href="whatsapp-marketing-services.html">WhatsApp Marketing</a></li>
            <li><a href="branding-and-design.html">Branding &amp; Design</a></li>
          </ul>
        </div>

        <div>
          <h4>Company</h4>
          <ul>
            <li><a href="about-us.html">About Us</a></li>
            <li><a href="services.html">Services</a></li>
            <li><a href="case-study.html">Case Studies</a></li>
            <li><a href="blog.html">Blog</a></li>
            <li><a href="faq.html">FAQ</a></li>
            <li><a href="contact-us.html">Contact</a></li>
          </ul>
        </div>

        <div>
          <h4>Get In Touch</h4>
          <div class="foot-contact-row">
            <span class="ic"><svg viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></span>
            <div><strong>Mumbai HQ</strong><a href="https://maps.google.com/?q=Ujagar+Chambers+Deonar+Chembur+Mumbai+400088" target="_blank" rel="noopener">1st Floor, Ujagar Chambers, Bus Depot, Sion&ndash;Trombay Rd, opp. Deonar, Chembur, Mumbai, Maharashtra 400088</a></div>
          </div>
          <div class="foot-contact-row">
            <span class="ic"><svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2z"/></svg></span>
            <div><strong>Phone</strong><a href="tel:+919956655662">+91 99566 55662</a><br><a href="tel:+917045337060">+91 70453 37060</a></div>
          </div>
          <div class="foot-contact-row">
            <span class="ic"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg></span>
            <div><strong>Email</strong><a href="mailto:info@digiveritaz.com">info@digiveritaz.com</a><br><a href="mailto:daniel@digiveritaz.com">daniel@digiveritaz.com</a><br><a href="mailto:durvamukherjee@digiveritaz.com">durvamukherjee@digiveritaz.com</a></div>
          </div>
        </div>

      </div>

      <div class="foot-mark" aria-hidden="true">
        <svg viewBox="0 0 1200 220" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="footMarkGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="rgba(15,23,42,.10)"/>
              <stop offset="1" stop-color="rgba(34,197,94,.18)"/>
            </linearGradient>
          </defs>
          <text x="600" y="180" text-anchor="middle" font-size="200" letter-spacing="-8">DIGIVERITAZ</text>
        </svg>
      </div>
    </div>

    <div class="foot-bottom">
      <span>© 2026 DigiVeritaz. All rights reserved.</span>
      <div class="foot-bottom-links">
        <a href="privacy-policy.html">Privacy Policy</a>
        <a href="terms-and-conditions.html">Terms &amp; Conditions</a>
        <a href="faq.html">FAQ</a>
      </div>
    </div>

  </div>
</footer>

<div class="lang-switcher" id="langSwitcher"></div>
<button class="to-top" aria-label="Back to top"><svg viewBox="0 0 24 24"><path d="M6 15l6-6 6 6"/></svg></button>

<script src="js/i18n.js?v={css_ver}"></script>
<script src="js/main.js?v={css_ver}"></script>
</body></html>
"""

def page_hero(title, crumb, intro=""):
    return f"""<section class="page-hero">
  <div class="container">
    <div class="breadcrumb">{crumb}</div>
    <h1 class="play">{title}</h1>
    {'<p class="lead">'+intro+'</p>' if intro else ''}
  </div>
</section>
"""

DEFAULT_KEYWORDS = "digital marketing agency India, digital marketing Mumbai, SEO agency India, PPC agency, performance marketing India, paid social media advertising, e-commerce marketing, WhatsApp marketing India, branding and design, data strategy consulting, DigiVeritaz"

def breadcrumb_jsonld(name, title):
    slug = name.replace(".html","")
    if slug == "index": return ""
    items = [
        {"@type":"ListItem","position":1,"name":"Home","item":SITE_URL+"/"},
        {"@type":"ListItem","position":2,"name":title.split("|")[0].strip(),"item":SITE_URL+"/"+slug+"/"}
    ]
    data = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items}
    return '<script type="application/ld+json">' + json.dumps(data, separators=(",",":")) + '</script>'

try:
    CSS_VER = int((OUT / "css" / "style.css").stat().st_mtime)
except Exception:
    CSS_VER = 1

def write(name, title, desc, body, keywords=None, extra_jsonld=""):
    kw = keywords or DEFAULT_KEYWORDS
    canonical = name.replace("index.html","") if name == "index.html" else name.replace(".html","/")
    crumb = breadcrumb_jsonld(name, title)
    head = HEAD_TPL.format(
        title=title, desc=desc, keywords=kw, canonical=canonical,
        nav="{nav}", extra_jsonld=(crumb + extra_jsonld),
        css_ver=CSS_VER,
    )
    head = head.replace("{nav}", build_nav(name))
    main = '\n<main id="main" role="main">\n'
    closemain = '\n</main>\n'
    (OUT / name).write_text(head + main + body + closemain + FOOT.replace("{css_ver}", str(CSS_VER)))

# ---------- ABOUT ----------
about_body = """
<section class="about-hero">
  <div class="container">
    <span class="kicker">About DigiVeritaz</span>
    <h1>Growth-Driven <span class="green_text">Digital Agency</span></h1>
    <p class="lead">We believe in marketing that <em>moves metrics</em> — not just minds. A performance marketing powerhouse fusing data, creativity, and accountability to deliver measurable business outcomes.</p>
    <div class="hero-sub">
      <span class="chip">15+ Years Experience</span>
      <span class="chip">AI-Infused Agility</span>
      <span class="chip">Performance-First</span>
    </div>
  </div>
</section>

<section class="about-stats">
  <div class="container">
    <div class="stat reveal"><div class="num">60<b>+</b></div><div class="lbl">Clients Across India</div></div>
    <div class="stat reveal delay-1"><div class="num">13<b>+</b></div><div class="lbl">Global Clients</div></div>
    <div class="stat reveal delay-2"><div class="num">15<b>+</b></div><div class="lbl">Years Experience</div></div>
    <div class="stat reveal delay-3"><div class="num">₹65Cr<b>+</b></div><div class="lbl">Revenue Generated</div></div>
    <div class="stat reveal delay-3"><div class="num">1.15L<b>+</b></div><div class="lbl">Leads Delivered</div></div>
    <div class="stat reveal delay-3"><div class="num">4–10<b>×</b></div><div class="lbl">ROAS Achieved</div></div>
  </div>
</section>

<section class="about-sec">
  <div class="container">
    <div class="sec-head reveal">
      <span class="kicker">Who We Are</span>
      <h2>Where marketing <span class="green_text">wisdom</span> meets modern <span class="green_text">agility</span></h2>
    </div>
    <div class="intro-lead reveal">We are a <strong>next-gen marketing agency</strong> that bridges the legacy of marketing wisdom with modern AI-infused agility. Our foundation rests on <strong>15+ years of cumulative experience</strong>, but our vision is future-forward — to drive real, measurable growth in a digital-first world.</div>
    <div class="mv-wrap reveal">
      <div class="mv-grid">
        <div class="mv-card mv-vision">
          <h3>Our Vision</h3>
          <p>To become a <strong>global benchmark in performance marketing</strong> by blending time-tested expertise, disruptive innovation, and data-driven intelligence — transforming how brands grow, engage, and convert in the digital age.</p>
        </div>
        <div class="mv-card mv-mission">
          <h3>Our Mission</h3>
          <p>To <strong>empower businesses with performance-driven marketing</strong> by leveraging AI, full-funnel strategies, and transparent accountability — ensuring every digital touchpoint drives real, measurable value.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="about-sec values-section">
  <div class="container">
    <div class="sec-head reveal">
      <span class="kicker">What We Stand For</span>
      <h2>Our Core <span class="green_text">Values</span></h2>
      <p>Six principles that shape every campaign we ship.</p>
    </div>
    <div class="values-grid">
      <div class="value-card reveal">
        <span class="val-num">01</span>
        <div class="val-icon"><svg viewBox="0 0 24 24"><path d="M3 20h18"/><rect x="5" y="12" width="3" height="7" rx="1"/><rect x="11" y="8" width="3" height="11" rx="1"/><rect x="17" y="4" width="3" height="15" rx="1"/></svg></div>
        <h3>Integrity Through Data</h3>
        <p>We let results speak — metrics and outcomes guide every decision we make.</p>
      </div>
      <div class="value-card reveal delay-1">
        <span class="val-num">02</span>
        <div class="val-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg></div>
        <h3>Legacy-Driven Innovation</h3>
        <p>We respect deep marketing principles while embracing new tools and methods.</p>
      </div>
      <div class="value-card reveal delay-2">
        <span class="val-num">03</span>
        <div class="val-icon"><svg viewBox="0 0 24 24"><path d="M13 2L5 14h6l-2 8 10-14h-6z"/></svg></div>
        <h3>Agility at the Core</h3>
        <p>We move fast, learn fast, and adapt quickly to every market shift.</p>
      </div>
      <div class="value-card reveal delay-1">
        <span class="val-num">04</span>
        <div class="val-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg></div>
        <h3>Client-Centric Growth</h3>
        <p>Every decision, campaign, and pivot centers on your customer's journey.</p>
      </div>
      <div class="value-card reveal delay-2">
        <span class="val-num">05</span>
        <div class="val-icon"><svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="3"/><circle cx="9" cy="12" r="1.2"/><circle cx="15" cy="12" r="1.2"/><path d="M12 5V2"/></svg></div>
        <h3>Tech-Led Excellence</h3>
        <p>Automation, attribution, and analytics form the backbone of everything we do.</p>
      </div>
      <div class="value-card reveal delay-3">
        <span class="val-num">06</span>
        <div class="val-icon"><svg viewBox="0 0 24 24"><path d="M3 12h18"/><path d="M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/><circle cx="12" cy="12" r="9"/></svg></div>
        <h3>Transparent Partnerships</h3>
        <p>Open dashboards, clear KPIs, and full visibility into our entire process.</p>
      </div>
    </div>
  </div>
</section>

<section class="process-section">
  <div class="container">
    <div class="sec-head reveal">
      <span class="kicker">Our Process</span>
      <h2>What We <span class="green_text">Do</span></h2>
      <p>A three-phase approach — Launch → Optimize → Scale — with defined steps to ensure consistency, clarity, and growth.</p>
    </div>
    <div class="process-track">
      <div class="phase-card reveal">
        <div class="phase-badge">01</div>
        <h3>Launch</h3>
        <ul>
          <li>Acquire platform, data and account access</li>
          <li>Perform audits across every platform</li>
          <li>Define campaign structures</li>
          <li>Develop creatives and copy</li>
          <li>Execute and launch campaigns</li>
        </ul>
      </div>
      <div class="phase-card reveal delay-1">
        <div class="phase-badge">02</div>
        <h3>Optimize</h3>
        <ul>
          <li>Ongoing audits and analytics</li>
          <li>Refine media planning and strategy</li>
          <li>Monitor daily performance and fine-tune</li>
          <li>Bi-weekly client review calls</li>
          <li>Reallocate or pause under-performers</li>
        </ul>
      </div>
      <div class="phase-card reveal delay-2">
        <div class="phase-badge">03</div>
        <h3>Scale</h3>
        <ul>
          <li>Identify top-performing campaigns</li>
          <li>Develop a roadmap and scaling plan</li>
          <li>Scale vertically (budget) and horizontally (reach)</li>
          <li>Deploy advanced reporting systems</li>
          <li>Execute the scaling roadmap strategically</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="services-expertise">
  <div class="container">
    <div class="sec-head reveal">
      <span class="kicker">Our Expertise</span>
      <h2>Full-Stack <span class="green_text">Service Suite</span></h2>
      <p>A broad set of digital marketing services, tailored to every stage of growth.</p>
    </div>
    <div class="expertise-grid">
      <a class="exp-card reveal" href="organic-marketing-services.html">
        <span class="exp-num">01</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><path d="M12 21c5-4 9-9 9-14 0-2-1-3-3-3-3 0-4 3-6 3s-3-3-6-3c-2 0-3 1-3 3 0 5 4 10 9 14z"/></svg></div>
        <h3>Organic Marketing</h3>
        <p>SEO, content, and social working together for long-term compounding growth.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal delay-1" href="paid-social-media-advertising.html">
        <span class="exp-num">02</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="3"/><circle cx="12" cy="12" r="3.5"/><circle cx="17" cy="7" r="1"/></svg></div>
        <h3>Paid Social Advertising</h3>
        <p>Meta, LinkedIn, Pinterest and Snapchat ads engineered to convert.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal delay-2" href="pay-per-click.html">
        <span class="exp-num">03</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div>
        <h3>Pay-Per-Click (PPC)</h3>
        <p>High-intent traffic via Google, Bing, Shopping and performance search.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal" href="performance-marketing-agency.html">
        <span class="exp-num">04</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><path d="M3 20h18"/><rect x="5" y="12" width="3" height="7" rx="1"/><rect x="11" y="8" width="3" height="11" rx="1"/><rect x="17" y="4" width="3" height="15" rx="1"/></svg></div>
        <h3>Performance Marketing</h3>
        <p>Full-funnel campaigns tied to CAC, ROAS and real revenue.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal delay-1" href="ecommerce-marketing.html">
        <span class="exp-num">05</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg></div>
        <h3>E-Commerce Platforms</h3>
        <p>Amazon, Flipkart, Shopify and D2C growth from listing to loyalty.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal delay-2" href="data-strategy-consulting-services.html">
        <span class="exp-num">06</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg></div>
        <h3>Data Strategy &amp; Consulting</h3>
        <p>Attribution, analytics and a measurement stack that drives decisions.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal" href="native-advertising.html">
        <span class="exp-num">07</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/><circle cx="7" cy="7.5" r="0.7"/></svg></div>
        <h3>Native Advertising</h3>
        <p>Premium publisher and marketplace placements that feel organic.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal delay-1" href="whatsapp-marketing-services.html">
        <span class="exp-num">08</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><path d="M4 11a8 8 0 1 1 3.5 6.6L3 19l1.4-4.2A7.9 7.9 0 0 1 4 11z"/></svg></div>
        <h3>WhatsApp Marketing</h3>
        <p>Conversational commerce, broadcasts and chatbot automation.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal delay-2" href="branding-and-design.html">
        <span class="exp-num">09</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><path d="M9 3l3 5 5 1-4 4 1 6-5-3-5 3 1-6-4-4 5-1z"/></svg></div>
        <h3>Branding &amp; Design</h3>
        <p>Research-led identity systems and creative direction that convert.</p>
        <span class="exp-link">Explore</span>
      </a>
      <a class="exp-card reveal delay-3" href="generative-search-optimisation.html">
        <span class="exp-num">10</span>
        <div class="exp-icon"><svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="3"/><circle cx="9" cy="12" r="1.2"/><circle cx="15" cy="12" r="1.2"/><path d="M12 5V2"/><path d="M2 12h2M20 12h2"/></svg></div>
        <h3>Generative Search Optimisation</h3>
        <p>Surface your brand in ChatGPT, Gemini, Perplexity and AI Overviews.</p>
        <span class="exp-link">Explore</span>
      </a>
    </div>
    <p class="svc-closing reveal delay-1">Whether you need to build awareness, drive conversions, or scale profits — we structure and sequence services based on what your business needs now… and in six months.</p>
  </div>
</section>

<section class="why-section">
  <div class="container">
    <div class="sec-head reveal">
      <span class="kicker">Why DigiVeritaz</span>
      <h2>Why brands <span class="green_text">choose us</span></h2>
    </div>
    <div class="why-grid">
      <div class="why-tile reveal"><div class="tile-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>We tie every campaign to business metrics — not vanity KPIs</p></div>
      <div class="why-tile reveal delay-1"><div class="tile-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>We back up strategies with data, not guesses</p></div>
      <div class="why-tile reveal delay-2"><div class="tile-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>Full visibility into performance via transparent dashboards</p></div>
      <div class="why-tile reveal delay-1"><div class="tile-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>AI and automation deployed to optimize at scale</p></div>
      <div class="why-tile reveal delay-2"><div class="tile-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>Agile methodology — we respond to market shifts quickly</p></div>
      <div class="why-tile reveal delay-3"><div class="tile-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>Deep experience balanced with fresh thinking</p></div>
    </div>
    <div class="why-promise reveal">We don't just promise performance — we guarantee <span class="green_text">direction, accountability, and growth.</span></div>
  </div>
</section>

<section class="about-cta">
  <div class="container reveal">
    <h2>Your brand's next big move <span>starts here</span></h2>
    <p>Let's talk growth. Book a discovery call and get a custom proposal within 48 hours.</p>
    <a class="btn" href="contact-us.html">Contact Us Today</a>
  </div>
</section>
"""
write("about-us.html",
      "About Digiveritaz | Digital Marketing Agency India",
      "Learn about Digiveritaz, an India-based digital marketing agency helping brands grow through SEO, paid ads, branding, and ROI-focused strategies.",
      about_body,
      keywords=DEFAULT_KEYWORDS + ", about DigiVeritaz, digital marketing agency Mumbai, performance marketing powerhouse, growth agency India, AI marketing agency")

# ---------- CONTACT ----------
contact_body = """
<section class="contact-hero">
  <div class="container">
    <nav class="cs-crumbs" aria-label="Breadcrumb">
      <a href="index.html"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11.5 12 4l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/></svg>Home</a>
      <span class="sep" aria-hidden="true">&rsaquo;</span>
      <span class="current" aria-current="page">Contact Us</span>
    </nav>
    <div><span class="cs-tag">Get in Touch</span></div>
    <h1 class="play">Your brand's next <span class="green_text">big move</span> starts here</h1>
    <p class="lead">Whether you're a startup, SME or global enterprise, DigiVeritaz turns your marketing budget into measurable business growth. Tell us about your goals &mdash; we'll respond within one business day.</p>
  </div>
</section>

<section class="contact-strip">
  <div class="container">
    <div class="strip-row">

      <div class="strip-item">
        <span class="sl">Phone</span>
        <a class="sv" href="tel:+919956655662">+91 99566 55662</a>
        <span class="sv-sub"><a href="tel:+917045337060">+91 70453 37060</a></span>
      </div>

      <div class="strip-item">
        <span class="sl">Email</span>
        <a class="sv" href="mailto:info@digiveritaz.com">info@digiveritaz.com</a>
        <span class="sv-sub"><a href="mailto:daniel@digiveritaz.com">daniel@digiveritaz.com</a> &middot; <a href="mailto:durvamukherjee@digiveritaz.com">durvamukherjee@digiveritaz.com</a></span>
      </div>

      <div class="strip-item">
        <span class="sl">Office</span>
        <a class="sv" href="https://maps.google.com/?q=Ujagar+Chambers+Deonar+Chembur+Mumbai+400088" target="_blank" rel="noopener">1st Floor, Ujagar Chambers</a>
        <span class="sv-sub">Bus Depot, Sion&ndash;Trombay Rd, opp. Deonar, Chembur, Mumbai, Maharashtra 400088<br>Mon&ndash;Sat &middot; 10:00 AM &ndash; 7:00 PM</span>
      </div>

    </div>
  </div>
</section>

<section class="contact-main">
  <div class="container">
    <div class="wrap">
      <div class="c-form-card">
        <div class="form-head">
          <div class="eyebrow">Let's Get Started</div>
          <h2>Tell us about your project</h2>
          <p>Share your goals, budget and timeline &mdash; we'll send a tailored proposal within one business day.</p>
        </div>
        <form id="contact-form" action="https://formsubmit.co/poojanvig.pv@gmail.com" method="POST">
          <input type="hidden" name="_subject" value="New lead from DigiVeritaz website">
          <input type="hidden" name="_template" value="table">
          <input type="hidden" name="_captcha" value="false">
          <input type="text" name="_honey" style="display:none">

          <div class="two-up">
            <div class="field">
              <label>Full Name <span class="req">*</span></label>
              <div class="input-wrap">
                <svg class="ico" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                <input type="text" name="fullname" placeholder="Your full name" required>
              </div>
            </div>
            <div class="field">
              <label>Email Address <span class="req">*</span></label>
              <div class="input-wrap">
                <svg class="ico" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>
                <input type="email" name="email" placeholder="you@company.com" required>
              </div>
            </div>
          </div>
          <div class="two-up" style="margin-top:16px">
            <div class="field">
              <label>Phone Number <span class="req">*</span></label>
              <div class="input-wrap">
                <svg class="ico" viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2z"/></svg>
                <input type="tel" name="phone" placeholder="+91 9XXXXXXXXX" required>
              </div>
            </div>
            <div class="field">
              <label>Company Name</label>
              <div class="input-wrap">
                <svg class="ico" viewBox="0 0 24 24"><path d="M3 21V7l9-4 9 4v14"/><path d="M9 21V11h6v10"/></svg>
                <input type="text" name="company" placeholder="Company">
              </div>
            </div>
          </div>

          <div class="field" style="margin-top:16px">
            <label>Budget Range</label>
            <select name="budget">
              <option value="">-- Please select budget range --</option>
              <option>INR 40k &ndash; 60k</option>
              <option>INR 60k to 1 Lac</option>
              <option>INR 1 Lac and above</option>
            </select>
          </div>

          <div class="section-label">Select the Services You Need</div>
          <div class="field">
            <div class="check-grid">
              <label><input type="checkbox" name="services[]" value="Organic Marketing"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Organic Marketing</label>
              <label><input type="checkbox" name="services[]" value="Paid Social Media"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Paid Social Media Advertising</label>
              <label><input type="checkbox" name="services[]" value="PPC"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Pay-Per-Click Advertising</label>
              <label><input type="checkbox" name="services[]" value="Performance Marketing"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Performance Marketing</label>
              <label><input type="checkbox" name="services[]" value="E-commerce"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>E-commerce Platforms</label>
              <label><input type="checkbox" name="services[]" value="Data Strategy"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Data Strategy &amp; Consulting</label>
              <label><input type="checkbox" name="services[]" value="Native Advertising"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Native Advertising</label>
              <label><input type="checkbox" name="services[]" value="WhatsApp"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>WhatsApp Marketing</label>
              <label><input type="checkbox" name="services[]" value="Branding"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Branding &amp; Design</label>
              <label><input type="checkbox" name="services[]" value="SEO"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Search Engine Optimization</label>
              <label><input type="checkbox" name="services[]" value="GSO"><span class="cbox"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></span>Generative Search Optimisation</label>
            </div>
          </div>

          <div class="field" style="margin-top:16px"><label>Project Brief</label><textarea name="message" rows="5" placeholder="Tentative start date, goals, platforms of interest, reference brands&hellip;"></textarea></div>

          <div class="submit-row">
            <button class="btn" type="submit">Send Request <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
            <span class="hint"><svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z" fill="none" stroke="currentColor"/><path d="M12 6v6l4 2" fill="none" stroke="currentColor"/></svg>We'll respond within one business day</span>
          </div>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="c-map">
  <div class="container">
    <div class="map-wrap">
      <iframe src="https://www.google.com/maps?q=Ujagar+Chambers,+Deonar,+Chembur,+Mumbai+400088&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="DigiVeritaz Mumbai Office Location"></iframe>
    </div>
  </div>
</section>
"""
contact_jsonld = '<script type="application/ld+json">' + json.dumps({
    "@context":"https://schema.org","@type":"ContactPage",
    "url": SITE_URL + "/contact-us/",
    "name": "Contact DigiVeritaz",
    "mainEntity": {"@id": SITE_URL + "/#organization"}
}, separators=(",",":")) + '</script>'
write("contact-us.html",
      "Contact Digiveritaz | Digital Marketing Agency India",
      "Get in touch with Digiveritaz to discuss SEO, PPC and performance marketing solutions for your business in India. Book a free 30-min strategy call today.",
      contact_body,
      keywords=DEFAULT_KEYWORDS + ", contact digital marketing agency, marketing agency Mumbai contact, free marketing proposal, digital marketing consultation",
      extra_jsonld=contact_jsonld)

# ---------- THANK YOU ----------
ty_body = """<section class="hero"><div class="container text-center">
<h1 class="play">Thank <span class="green_text">You!</span></h1>
<p class="lead" style="margin:0 auto">We've received your message and will get back to you shortly. If your inquiry is urgent, please call us directly at <a href="tel:+919956655662">+91 99566 55662</a> or <a href="tel:+917045337060">+91 70453 37060</a>.</p>
<div class="mt-20"><a class="btn" href="index.html">Back to Home</a></div>
</div></section>"""
write("thank-you.html", "Thank You | DigiVeritaz",
      "Thank you for contacting DigiVeritaz. We'll respond within one business day.",
      ty_body)

# ---------- SERVICES HUB ----------
# Card-icon SVGs keyed by SVC_CARD_META[..][0] (icon-key from services_data).
SVC_ICON = {
    "seo":        '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    "ppc":        '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "perf":       '<svg viewBox="0 0 24 24"><path d="M3 20h18"/><rect x="5" y="12" width="3" height="7" rx="1"/><rect x="11" y="8" width="3" height="11" rx="1"/><rect x="17" y="4" width="3" height="15" rx="1"/></svg>',
    "social":     '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="3"/><circle cx="12" cy="12" r="3.5"/><circle cx="17" cy="7" r="1"/></svg>',
    "ecom":       '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg>',
    "cart":       '<svg viewBox="0 0 24 24"><circle cx="9" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/><path d="M3 4h2l3 12h11l2-8H6"/></svg>',
    "whatsapp":   '<svg viewBox="0 0 24 24"><path d="M4 11a8 8 0 1 1 3.5 6.6L3 19l1.4-4.2A7.9 7.9 0 0 1 4 11z"/></svg>',
    "native":     '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/><circle cx="7" cy="7.5" r="0.7"/></svg>',
    "organic":    '<svg viewBox="0 0 24 24"><path d="M12 21c5-4 9-9 9-14 0-2-1-3-3-3-3 0-4 3-6 3s-3-3-6-3c-2 0-3 1-3 3 0 5 4 10 9 14z"/></svg>',
    "brand":      '<svg viewBox="0 0 24 24"><path d="M9 3l3 5 5 1-4 4 1 6-5-3-5 3 1-6-4-4 5-1z"/></svg>',
    "ai":         '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="3"/><circle cx="9" cy="12" r="1.2"/><circle cx="15" cy="12" r="1.2"/><path d="M12 5V2"/><path d="M2 12h2M20 12h2"/></svg>',
    "data":       '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>',
    "influencer": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/><path d="M19 4l1 2 2 1-2 1-1 2-1-2-2-1 2-1z"/></svg>',
    "pr":         '<svg viewBox="0 0 24 24"><path d="M3 11l13-7v16L3 13z"/><rect x="6" y="11" width="3" height="5"/><path d="M16 8a3 3 0 0 1 0 8"/></svg>',
    "orm":        '<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M9 12l2 2 4-4"/></svg>',
    "content":    '<svg viewBox="0 0 24 24"><path d="M4 4h16v4H4zM4 12h10v4H4zM4 20h16"/></svg>',
    "uiux":       '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="2"/><path d="M3 9h18"/><path d="M8 21h8"/><path d="M12 17v4"/></svg>',
    "product":    '<svg viewBox="0 0 24 24"><path d="M3 7l9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7"/><path d="M12 11v10"/></svg>',
    "comm":       '<svg viewBox="0 0 24 24"><path d="M3 5h12l5 5-5 5H3z"/><path d="M7 9h6M7 12h4"/></svg>',
    "copy":       '<svg viewBox="0 0 24 24"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>',
    "display":    '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/></svg>',
    "meta":       '<svg viewBox="0 0 24 24"><path d="M3 12c2-6 7-7 9-1 2 6 7 5 9-1"/><circle cx="6" cy="11" r="1.5"/><circle cx="18" cy="13" r="1.5"/></svg>',
    "shopping":   '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg>',
    "cro":        '<svg viewBox="0 0 24 24"><path d="M3 17l6-6 4 4 8-8"/><path d="M17 7h4v4"/></svg>',
    "revenue":    '<svg viewBox="0 0 24 24"><path d="M12 2v20"/><path d="M17 6H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H7"/></svg>',
    "lead":       '<svg viewBox="0 0 24 24"><path d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z"/><path d="M10 10l4 4"/></svg>',
    "cmo":        '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/><path d="M9 8l2 2 4-4"/></svg>',
    "page":       '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
    "realestate": '<svg viewBox="0 0 24 24"><path d="M3 11l9-7 9 7v9a2 2 0 0 1-2 2h-4v-6h-6v6H5a2 2 0 0 1-2-2z"/></svg>',
    "research":   '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/><path d="M9 11h4M11 9v4"/></svg>',
    "strategy":   '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg>',
    "analytics":  '<svg viewBox="0 0 24 24"><path d="M3 20h18"/><path d="M5 16l4-6 4 4 6-9"/></svg>',
    "gtm":        '<svg viewBox="0 0 24 24"><path d="M12 2L2 12l10 10 10-10z"/><path d="M9 12l2 2 4-4"/></svg>',
    "web":        '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a13 13 0 0 1 0 18 13 13 0 0 1 0-18z"/></svg>',
    "software":   '<svg viewBox="0 0 24 24"><path d="M9 8l-5 4 5 4M15 8l5 4-5 4M14 4l-4 16"/></svg>',
    "wp":         '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3.5 12L9 21M14.5 4L19 18M9 21l4-12 4 9"/></svg>',
    "mobile":     '<svg viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2"/><circle cx="12" cy="18" r="1"/></svg>',
    "server":     '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><circle cx="7" cy="7" r="1"/><circle cx="7" cy="17" r="1"/></svg>',
    "email":      '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    "crm":        '<svg viewBox="0 0 24 24"><circle cx="9" cy="9" r="3"/><path d="M3 21c0-3 3-6 6-6s6 3 6 6"/><path d="M16 11l3 3 4-4"/></svg>',
}

SERVICE_IMAGE_MAP = {
    slug: "assets/services/" + slug.replace(".html", ".webp")
    for slug in SERVICE_TITLE_MAP
}

CATEGORY_BLURBS = {
    "Marketing": "Organic demand, creator trust, AI visibility and lifecycle channels for brands that want compounding attention.",
    "Advertising": "Paid media systems built for intent, marketplace demand, retargeting and measurable acquisition.",
    "Design & Content": "Visual identity, product experience and persuasive content shaped for conversion and recall.",
    "Strategy & Data": "Planning, analytics and revenue systems that turn scattered activity into a measurable growth engine.",
    "Tech & Development": "Websites, commerce, apps, hosting, CRM and business systems built to perform after launch.",
}

def _strip_tags(s): return _pre_re.sub(r'<[^>]+>','',s).replace('&amp;','&').strip()

def _svc_card(slug, category="", idx=0):
    icon_key, blurb = SVC_CARD_META.get(_doc_slug_for(slug), ("seo", ""))
    title = SERVICE_TITLE_MAP.get(slug, slug)
    img = SERVICE_IMAGE_MAP.get(slug, "")
    alt = _strip_tags(title)
    cls = "svc-card" + (" svc-card-featured" if idx == 0 else "")
    cat_label = category or "Service"
    return (
        f'<a class="{cls}" href="{slug}">'
        f'<span class="svc-card-media"><img src="{img}" alt="{alt}" loading="lazy" decoding="async"></span>'
        f'<span class="svc-card-body">'
        f'<span class="svc-card-kicker"><span class="icon">{SVC_ICON.get(icon_key, SVC_ICON["seo"])}</span>{cat_label}</span>'
        f'<span class="svc-card-title">{title}</span>'
        f'<span class="svc-card-copy">{blurb}</span>'
        f'<span class="more">Explore service <span aria-hidden="true">&rarr;</span></span>'
        f'</span>'
        f'</a>'
    )

# Build a reverse map: site_slug -> doc_slug, used to find icon/blurb in CARD_META.
_SLUG_REVERSE = {svc["site_slug"]: svc["doc_slug"] for svc in DOC_SERVICES}
def _doc_slug_for(site_slug):
    return _SLUG_REVERSE.get(site_slug, "/SEO")

def _cat_key(name):
    return _pre_re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

_TAB_ICONS = {
    "all":               '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
    "marketing":         '<svg viewBox="0 0 24 24"><path d="M3 11l16-7v18l-16-7z"/><path d="M3 11h6l3 8"/></svg>',
    "advertising":       '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg>',
    "design-content":    '<svg viewBox="0 0 24 24"><path d="M12 2c-5 0-9 4-9 9 0 4 3 7 7 7 1 0 2-1 2-2 0-2 2-2 2-4 0-3 4-3 4-5 0-3-3-5-6-5z"/><circle cx="7" cy="11" r="1.2"/><circle cx="10" cy="7" r="1.2"/><circle cx="14" cy="7" r="1.2"/><circle cx="17" cy="11" r="1.2"/></svg>',
    "strategy-data":     '<svg viewBox="0 0 24 24"><path d="M3 20h18"/><rect x="5" y="12" width="3" height="7" rx=".6"/><rect x="11" y="7" width="3" height="12" rx=".6"/><rect x="17" y="3" width="3" height="16" rx=".6"/></svg>',
    "tech-development":  '<svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/><line x1="14.5" y1="4" x2="9.5" y2="20"/></svg>',
}

# Total service count
_svc_count_total = sum(len(s) for _, s in SVC_CATEGORIES)

def _svc_tab_html(key, label, count, active=False):
    icon = _TAB_ICONS.get(key, _TAB_ICONS["all"])
    cls = "svc-tab" + (" active" if active else "")
    aria = "true" if active else "false"
    return (
        f'<button type="button" class="{cls}" data-target="{key}" role="tab" aria-selected="{aria}">'
        f'<span class="svc-tab-icon">{icon}</span>'
        f'<span class="svc-tab-label">{label}</span>'
        f'<span class="svc-tab-count">{count}</span>'
        f'</button>'
    )

_svc_tabs_html = (
    '<div class="svc-tabs reveal" role="tablist">'
    + _svc_tab_html("all", "All Services", _svc_count_total, active=True)
    + "".join(
        _svc_tab_html(_cat_key(_cat), _cat, len(_slugs))
        for _cat, _slugs in SVC_CATEGORIES
    )
    + '</div>'
)

cat_groups_html = []
for _cat, _slugs in SVC_CATEGORIES:
    cards = "".join(_svc_card(s, _cat, i) for i, s in enumerate(_slugs))
    key = _cat_key(_cat)
    blurb = CATEGORY_BLURBS.get(_cat, "")
    cat_groups_html.append(
        f'<div class="svc-cat-group reveal" id="{key}" data-cat="{key}">'
        f'<div class="svc-cat-head-row">'
        f'<div><span class="svc-cat-eyebrow">{len(_slugs)} services</span>'
        f'<h2 class="svc-cat-head">{_cat}</h2>'
        f'<p class="svc-cat-desc">{blurb}</p></div>'
        f'<a class="svc-cat-jump" href="#{key}">View {len(_slugs)}</a>'
        f'</div>'
        f'<div class="services-grid">{cards}</div>'
        f'</div>'
    )
svc_groups_html = "".join(cat_groups_html)

# Inline JS — toggles which category groups are visible based on the active tab.
_svc_tabs_script = """
<script>
(function(){
  var tabs = document.querySelectorAll('.svc-tab');
  var groups = document.querySelectorAll('.svc-cat-group');
  function activate(target){
    tabs.forEach(function(t){
      var on = t.dataset.target === target;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    groups.forEach(function(g){
      var show = (target === 'all') || (g.dataset.cat === target);
      g.style.display = show ? '' : 'none';
      if (show){
        g.classList.remove('svc-fade-in');
        // re-trigger fade-in animation
        // eslint-disable-next-line no-unused-expressions
        void g.offsetWidth;
        g.classList.add('svc-fade-in');
      }
    });
    // Persist via hash so links can deep-link to a category
    if (target && target !== 'all'){
      history.replaceState(null, '', '#' + target);
    } else {
      history.replaceState(null, '', location.pathname);
    }
  }
  tabs.forEach(function(t){
    t.addEventListener('click', function(){ activate(t.dataset.target); });
  });
  // Honour deep-link hash on load
  var initial = (location.hash || '').replace('#','');
  if (initial){
    var ok = Array.prototype.some.call(tabs, function(t){ return t.dataset.target === initial; });
    if (ok){ activate(initial); }
  }
})();
</script>
"""

svc_body = f"""
<section class="svc-hub-hero">
  <div class="svc-hub-hero-media" aria-hidden="true">
    <img src="assets/services/performance-marketing-agency.webp" alt="">
  </div>
  <div class="container">
    <nav class="breadcrumb">Home / Services</nav>
    <span class="svc-hero-kicker">41 services across 5 growth disciplines</span>
    <h1 class="play">Choose the service stack that moves your next number.</h1>
    <p>Browse strategy, media, design, data and development offers built around measurable growth. Pick one specialist service or hand us the whole engine.</p>
    <div class="svc-hero-actions">
      <a class="btn" href="contact-us.html">Build My Growth Plan</a>
      <a class="btn-outline btn-ghost" href="#all-services">Browse Services</a>
    </div>
  </div>
</section>
<section class="services svc-hub">
  <div class="container" id="all-services">
    {_svc_tabs_html}
    <div class="svc-cat-wrap">{svc_groups_html}</div>
  </div>
</section>
<section class="svc-hub-cta">
  <div class="container">
    <h2 class="play">Not sure where to start?</h2>
    <p>Tell us your target, budget and current stack. We will shape the right service mix before you spend.</p>
    <a class="btn" href="contact-us.html">Book A Call</a>
  </div>
</section>
{_svc_tabs_script}
"""
write("services.html",
      "Best Digital Marketing Services in India | Digiveritaz",
      "Explore Digiveritaz full-suite digital marketing services in India including SEO, PPC, performance marketing, paid social, WhatsApp marketing and branding.",
      svc_body,
      keywords=DEFAULT_KEYWORDS + ", digital marketing services, marketing services India, full service marketing agency, marketing packages Mumbai")

# ---------- INDIVIDUAL SERVICE PAGES ----------
# Individual service pages are now generated from doc-driven data
# (services_data.SERVICES). The old per-service dict has been replaced.

import re as _pre_re
def _strip_tags(s): return _pre_re.sub(r'<[^>]+>','',s).replace('&amp;','&').strip()

HERO_ORBS = """  <span class="hero-orb-1" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2l2.8 7h7l-5.7 4.2 2.2 7.2L12 16.6l-6.3 3.8 2.2-7.2L2.2 9h7z"/></svg></span>
  <span class="hero-orb-2" aria-hidden="true"><svg viewBox="0 0 60 60"><path d="M30 4 C 48 6 56 18 56 30 C 56 44 46 56 30 56 C 14 56 4 44 4 30 C 4 18 12 6 30 4 Z"/></svg></span>
  <span class="hero-orb-3" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2C8 6 4 10 4 14c0 5 4 8 8 8s8-3 8-8c0-4-4-8-8-12z"/></svg></span>
  <span class="hero-orb-4" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/></svg></span>
"""

MARQUEE_ITEMS = ["Performance-First", "Data-Driven", "Results That Compound", "Human + AI", "ROI Over Vanity", "Transparent Dashboards", "15+ Years Experience"]

def render_eeat(rows):
    if not rows: return ""
    cards = []
    for r in rows:
        cards.append(
            '<div class="eeat-card reveal">'
            f'<span class="eeat-marker" aria-hidden="true">{r["marker"]}</span>'
            f'<span class="eeat-tag">{r["pillar"]}</span>'
            f'<h3 class="eeat-signal">{r["signal"]}</h3>'
            f'<p class="eeat-evidence">{r["evidence"]}</p>'
            '</div>'
        )
    return (
        '<section class="eeat-section">'
        '<div class="container">'
        '<div class="sec-head reveal"><span class="kicker">E-E-A-T Trust Signals</span>'
        '<h2>How We Earn <span class="green_text">Your Confidence</span></h2>'
        '<p>The four signals below show how we demonstrate Experience, Expertise, '
        'Authoritativeness, and Trustworthiness on this service — visible to both users and search engines.</p>'
        '</div>'
        + '<div class="eeat-grid">' + "".join(cards) + '</div>'
        + '</div>'
        + '</section>'
    )

def _split_label(text):
    """Split 'Label — body' into (label, body) when a clean dash separator is
    present; otherwise return (None, text)."""
    for sep in (" — ", " – "):
        if sep in text:
            head, rest = text.split(sep, 1)
            if 2 <= len(head) <= 70:
                return head, rest
    return None, text

def _group_sections(blocks):
    """Group flat block list into [{heading, kicker, paras, bullets, sub:[(h3,p),...]}, ...]."""
    sections = []
    cur = None
    pending_h3 = None  # current sub-heading awaiting its paragraph
    def new_section(heading=None):
        return {"heading": heading, "paras": [], "bullets": [], "sub": []}
    cur = new_section()
    for kind, text in blocks:
        if kind == "h2":
            if cur["heading"] or cur["paras"] or cur["bullets"] or cur["sub"]:
                sections.append(cur)
            cur = new_section(text)
            pending_h3 = None
        elif kind == "h3":
            pending_h3 = text
        elif kind == "p":
            if pending_h3 is not None:
                cur["sub"].append((pending_h3, text))
                pending_h3 = None
            else:
                cur["paras"].append(text)
        elif kind == "li":
            if pending_h3 is not None:
                # rare: a bullet appeared right after an h3 with no paragraph;
                # treat the h3 itself as a bullet to avoid swallowing the line.
                cur["bullets"].append(pending_h3)
                pending_h3 = None
            cur["bullets"].append(text)
    if pending_h3 is not None:
        cur["bullets"].append(pending_h3)
    if cur["heading"] or cur["paras"] or cur["bullets"] or cur["sub"]:
        sections.append(cur)
    return sections

# --------- Section layouts ------------------------------------------

def _intro_html(paras):
    if not paras: return ""
    return '<p class="svc-sec-intro">' + paras[0] + '</p>' + (
        "".join(f'<p>{x}</p>' for x in paras[1:])
    )

_NUMBER_PATHS = [
    # 12 distinct minimalist line icons keyed off section index
    "M3 20h18M5 12v7M11 8v11M17 4v15",
    "M12 2a10 10 0 1 0 10 10M12 6v6l4 2",
    "M13 2L5 14h6l-2 8 10-14h-6z",
    "M12 21c5-4 9-9 9-14 0-2-1-3-3-3-3 0-4 3-6 3s-3-3-6-3c-2 0-3 1-3 3 0 5 4 10 9 14z",
    "M20 6L9 17l-5-5",
    "M12 2L15 8l6 1-4 4 1 6-6-3-6 3 1-6-4-4 6-1z",
    "M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7zM8 7V5a3 3 0 0 1 6 0v2",
    "M3 11l9-7 9 7v9a2 2 0 0 1-2 2h-4v-6h-6v6H5a2 2 0 0 1-2-2z",
    "M4 4h16v4H4zM4 12h10v4H4zM4 20h16",
    "M3 17l6-6 4 4 8-8M17 7h4v4",
    "M12 2v20M17 6H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H7",
    "M5 4h14M5 12h14M5 20h14",
]

def _sec_icon_svg(idx):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{_NUMBER_PATHS[idx % len(_NUMBER_PATHS)]}"/></svg>'

def _sec_header(heading, idx):
    if not heading: return ""
    num = f'{(idx+1):02d}'
    return (
        '<div class="svc-sec-head reveal">'
        f'<span class="svc-sec-num">{num}</span>'
        f'<h2>{heading}</h2>'
        '</div>'
    )

def _section_wrap(idx, inner, extra_class=""):
    cls = "svc-doc-sec" + (" alt" if idx % 2 else "") + (f" {extra_class}" if extra_class else "")
    return f'<section class="{cls}"><div class="container">{inner}</div></section>'

# Layout A: visual process timeline (sub-blocks like Phase/Step/Tier)
def _layout_subgrid(sec, idx):
    head = _sec_header(sec["heading"], idx)
    intro = _intro_html(sec["paras"])
    arrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    steps = []
    for i, (label, body) in enumerate(sec["sub"]):
        # Strip the "Phase N — " prefix so the heading reads cleanly.
        clean = _pre_re.sub(r'^(Phase|Step|Tier|Stage|Module|Level|Track)\s+\w{1,4}\s*[—–:\-]\s*',
                       '', label, flags=_pre_re.IGNORECASE)
        kicker_word = label.split()[0].title() if label.split() else "Step"
        steps.append(
            f'<div class="svc-tl-step reveal">'
            f'<div class="svc-tl-marker"><span class="svc-tl-num">{(i+1):02d}</span></div>'
            f'<span class="svc-tl-arrow">{arrow}</span>'
            f'<div class="svc-tl-card">'
            f'<span class="svc-tl-kicker">{kicker_word} {(i+1):02d}</span>'
            f'<h3>{clean}</h3>'
            f'<p>{body}</p>'
            f'</div>'
            f'</div>'
        )
    bullets_html = ""
    if sec["bullets"]:
        bullets_html = _layout_bullets_html(sec["bullets"])
    return _section_wrap(
        idx,
        head
        + (f'<div class="svc-sec-intro-wrap reveal">{intro}</div>' if intro else "")
        + f'<div class="svc-tl-track">{"".join(steps)}</div>'
        + bullets_html,
    )

_INDUSTRY_ICONS = {
    "e-commerce":   '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg>',
    "ecommerce":    '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg>',
    "real estate":  '<svg viewBox="0 0 24 24"><path d="M3 11l9-7 9 7v9a2 2 0 0 1-2 2h-4v-6h-6v6H5a2 2 0 0 1-2-2z"/></svg>',
    "property":     '<svg viewBox="0 0 24 24"><path d="M3 11l9-7 9 7v9a2 2 0 0 1-2 2h-4v-6h-6v6H5a2 2 0 0 1-2-2z"/></svg>',
    "healthcare":   '<svg viewBox="0 0 24 24"><path d="M12 2v20M2 12h20"/><circle cx="12" cy="12" r="9"/></svg>',
    "health":       '<svg viewBox="0 0 24 24"><path d="M12 2v20M2 12h20"/><circle cx="12" cy="12" r="9"/></svg>',
    "clinic":       '<svg viewBox="0 0 24 24"><path d="M12 2v20M2 12h20"/><circle cx="12" cy="12" r="9"/></svg>',
    "finance":      '<svg viewBox="0 0 24 24"><path d="M12 2v20"/><path d="M17 6H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H7"/></svg>',
    "fintech":      '<svg viewBox="0 0 24 24"><path d="M12 2v20"/><path d="M17 6H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H7"/></svg>',
    "banking":      '<svg viewBox="0 0 24 24"><path d="M12 2v20"/><path d="M17 6H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H7"/></svg>',
    "education":    '<svg viewBox="0 0 24 24"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v6c2 1 4 1.5 6 1.5s4-.5 6-1.5v-6"/></svg>',
    "edtech":       '<svg viewBox="0 0 24 24"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v6c2 1 4 1.5 6 1.5s4-.5 6-1.5v-6"/></svg>',
    "b2b":          '<svg viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/></svg>',
    "saas":         '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M7 14h6"/></svg>',
    "hospitality":  '<svg viewBox="0 0 24 24"><path d="M4 21V8M20 21V8M4 8h16M8 8V4h8v4M10 14h4M10 18h4"/></svg>',
    "travel":       '<svg viewBox="0 0 24 24"><path d="M2 12c4-6 8-8 10-8s6 2 10 8c-4 6-8 8-10 8s-6-2-10-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "fashion":      '<svg viewBox="0 0 24 24"><path d="M9 3l3 3 3-3 4 5-3 2v11H8V10L5 8z"/></svg>',
    "lifestyle":    '<svg viewBox="0 0 24 24"><path d="M9 3l3 3 3-3 4 5-3 2v11H8V10L5 8z"/></svg>',
    "d2c":          '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/></svg>',
    "fmcg":         '<svg viewBox="0 0 24 24"><rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9 7h6M9 11h6M9 15h4"/></svg>',
    "food":         '<svg viewBox="0 0 24 24"><path d="M5 11a7 7 0 0 1 14 0v3H5z"/><path d="M3 16h18M5 19h14"/></svg>',
    "beauty":       '<svg viewBox="0 0 24 24"><path d="M12 2C8 5 6 8 6 12a6 6 0 0 0 12 0c0-4-2-7-6-10z"/></svg>',
    "wellness":     '<svg viewBox="0 0 24 24"><path d="M12 21c5-4 9-9 9-14 0-2-1-3-3-3-3 0-4 3-6 3s-3-3-6-3c-2 0-3 1-3 3 0 5 4 10 9 14z"/></svg>',
    "fitness":      '<svg viewBox="0 0 24 24"><path d="M2 12h2M20 12h2M6 7v10M18 7v10M9 10h6M9 14h6"/></svg>',
    "tech":         '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>',
    "gadget":       '<svg viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2"/><circle cx="12" cy="18" r="1"/></svg>',
    "professional": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>',
    "automotive":   '<svg viewBox="0 0 24 24"><path d="M3 16v-4l3-5h12l3 5v4"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>',
    "manufacturing":'<svg viewBox="0 0 24 24"><path d="M3 21V8l5 3V8l5 3V8l8 3v10z"/></svg>',
    "consumer":     '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg>',
}

def _industry_icon(label):
    """Pick an icon SVG for an industry label by keyword match."""
    low = label.lower()
    for key, svg in _INDUSTRY_ICONS.items():
        if key in low:
            return svg
    # Default: tag icon
    return '<svg viewBox="0 0 24 24"><path d="M20 12L12 4H4v8l8 8z"/><circle cx="9" cy="9" r="1.5"/></svg>'

# Layout B: industry/category icon cards (replaces flat pill cloud)
def _layout_pills(sec, idx):
    head = _sec_header(sec["heading"], idx)
    intro = _intro_html(sec["paras"])
    cards = []
    for b in sec["bullets"]:
        # Industries are short labels — split on common separators if present
        cards.append(
            '<div class="svc-ind-card reveal">'
            f'<div class="svc-ind-icon">{_industry_icon(b)}</div>'
            f'<span class="svc-ind-label">{b}</span>'
            '</div>'
        )
    return _section_wrap(
        idx,
        head
        + (f'<div class="svc-sec-intro-wrap reveal">{intro}</div>' if intro else "")
        + f'<div class="svc-ind-grid reveal">{"".join(cards)}</div>',
        extra_class="industries",
    )

_CHECK_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<polyline points="20 6 9 17 4 12"/></svg>'
)

# Layout C: feature card grid (bullets with "Label — body" pattern)
def _layout_feature_cards(sec, idx):
    head = _sec_header(sec["heading"], idx)
    intro = _intro_html(sec["paras"])
    cards = []
    for b in sec["bullets"]:
        label, body = _split_label(b)
        if label:
            cards.append(
                '<div class="svc-feat-card reveal">'
                f'<span class="svc-feat-icon">{_CHECK_SVG}</span>'
                '<div class="svc-feat-content">'
                f'<h3>{label}</h3>'
                f'<p>{body}</p>'
                '</div>'
                '</div>'
            )
        else:
            cards.append(
                '<div class="svc-feat-card reveal plain">'
                f'<span class="svc-feat-icon">{_CHECK_SVG}</span>'
                '<div class="svc-feat-content">'
                f'<p>{b}</p>'
                '</div>'
                '</div>'
            )
    return _section_wrap(
        idx,
        head
        + (f'<div class="svc-sec-intro-wrap reveal">{intro}</div>' if intro else "")
        + f'<div class="svc-feat-grid">{"".join(cards)}</div>',
    )

# Layout D: check-tile grid (short uniform bullets)
def _layout_checks(sec, idx):
    head = _sec_header(sec["heading"], idx)
    intro = _intro_html(sec["paras"])
    tiles = "".join(
        '<div class="svc-check-tile reveal">'
        f'<span class="svc-feat-icon">{_CHECK_SVG}</span>'
        f'<p>{b}</p>'
        '</div>'
        for b in sec["bullets"]
    )
    return _section_wrap(
        idx,
        head
        + (f'<div class="svc-sec-intro-wrap reveal">{intro}</div>' if intro else "")
        + f'<div class="svc-check-grid reveal">{tiles}</div>',
    )

# Layout E: prose only (heading + paragraphs)
def _layout_prose(sec, idx):
    head = _sec_header(sec["heading"], idx)
    body = "".join(f'<p>{p}</p>' for p in sec["paras"])
    return _section_wrap(
        idx,
        head + f'<div class="svc-prose reveal">{body}</div>',
    )

def _layout_bullets_html(bullets):
    """Reusable bullets renderer when bullets coexist with sub-grid (Layout A)."""
    items = []
    for b in bullets:
        label, body = _split_label(b)
        if label:
            items.append(f'<li><strong>{label}</strong> — {body}</li>')
        else:
            items.append(f'<li>{b}</li>')
    return f'<ul class="svc-list reveal">{"".join(items)}</ul>'

# --------- Layout chooser -------------------------------------------

def _is_industries_themed(sec):
    h = (sec["heading"] or "").lower()
    return (
        any(h.startswith(s) for s in ("industries ", "categories ", "sectors ", "verticals ", "creator categories"))
        or " industries" in h or " categories" in h or " sectors" in h or " verticals" in h
    )

def _is_pills_section(sec):
    if not sec["bullets"]: return False
    if not _is_industries_themed(sec): return False
    # Plain short labels without em-dash → industry icon grid
    if all(_split_label(b)[0] is None for b in sec["bullets"]) \
       and all(len(b) <= 80 for b in sec["bullets"]):
        return True
    return False

def _is_feature_cards_section(sec):
    if len(sec["bullets"]) < 3: return False
    labelled = sum(1 for b in sec["bullets"] if _split_label(b)[0] is not None)
    return labelled >= max(3, int(0.6 * len(sec["bullets"])))

def _layout_quote(sec, idx):
    """Quote-styled lead section — used for the first body section
    when it has no heading (pre-section narrative)."""
    paras = sec["paras"]
    if not paras: return ""
    primary = paras[0]
    rest = "".join(f'<p>{p}</p>' for p in paras[1:])
    return (
        '<section class="svc-quote-sec">'
        '<div class="container">'
        '<div class="svc-quote-card reveal">'
        '<svg class="svc-quote-mark" viewBox="0 0 32 32" aria-hidden="true">'
        '<path d="M9 8c-3 0-5 2-5 6v10h8V14H8c0-3 1-4 3-4zM23 8c-3 0-5 2-5 6v10h8V14h-4c0-3 1-4 3-4z"/>'
        '</svg>'
        f'<p class="svc-quote-text">{primary}</p>'
        f'{rest}'
        '</div>'
        '</div>'
        '</section>'
    )

# Layout F: industry cards with descriptions (industries section + em-dash labels)
def _layout_industry_features(sec, idx):
    head = _sec_header(sec["heading"], idx)
    intro = _intro_html(sec["paras"])
    cards = []
    for b in sec["bullets"]:
        label, body = _split_label(b)
        if label:
            cards.append(
                '<div class="svc-ind-feat-card reveal">'
                f'<div class="svc-ind-icon">{_industry_icon(label)}</div>'
                '<div class="svc-ind-feat-content">'
                f'<h3>{label}</h3>'
                f'<p>{body}</p>'
                '</div>'
                '</div>'
            )
        else:
            cards.append(
                '<div class="svc-ind-feat-card reveal">'
                f'<div class="svc-ind-icon">{_industry_icon(b)}</div>'
                '<div class="svc-ind-feat-content">'
                f'<h3>{b}</h3>'
                '</div>'
                '</div>'
            )
    return _section_wrap(
        idx,
        head
        + (f'<div class="svc-sec-intro-wrap reveal">{intro}</div>' if intro else "")
        + f'<div class="svc-ind-feat-grid reveal">{"".join(cards)}</div>',
        extra_class="industries",
    )

def render_doc_blocks(blocks):
    sections = _group_sections(blocks)
    out = []
    for i, sec in enumerate(sections):
        if i == 0 and not sec["heading"] and sec["paras"] and not sec["bullets"] and not sec["sub"]:
            out.append(_layout_quote(sec, i))
            continue
        if sec["sub"]:
            out.append(_layout_subgrid(sec, i))
        elif _is_pills_section(sec):
            out.append(_layout_pills(sec, i))
        elif _is_industries_themed(sec) and sec["bullets"]:
            out.append(_layout_industry_features(sec, i))
        elif _is_feature_cards_section(sec):
            out.append(_layout_feature_cards(sec, i))
        elif sec["bullets"]:
            out.append(_layout_checks(sec, i))
        else:
            out.append(_layout_prose(sec, i))
    return "".join(out)

SVC_STATS = [
    ("80+",   "Brands trust us"),
    ("120+",  "Page-1 keyword rankings"),
    ("4.9★",  "Google rating (600+ reviews)"),
    ("6+",    "Years in active client work"),
]

def render_stats_strip():
    cells = "".join(
        f'<div class="svc-stat reveal{(" delay-"+str(i)) if i else ""}">'
        f'<div class="svc-stat-num">{n}</div>'
        f'<div class="svc-stat-lbl">{l}</div>'
        f'</div>'
        for i,(n,l) in enumerate(SVC_STATS)
    )
    return (
        '<section class="svc-stats-strip">'
        '<div class="container">'
        f'<div class="svc-stats-grid">{cells}</div>'
        '</div>'
        '</section>'
    )

def _svc_img(slug):
    return SERVICE_IMAGE_MAP.get(slug, "assets/services/seo.webp")

def _find_section(sections, needle):
    needle = needle.lower()
    for sec in sections:
        if needle in (sec.get("heading") or "").lower():
            return sec
    return None

def _v2_stat_cards():
    stats = [
        ("120+", "Page 1 rankings"),
        ("80+", "Brands served"),
        ("₹2Cr+", "Organic revenue attributed"),
        ("4.9★", "600+ review rating"),
    ]
    return "".join(
        f'<div class="svc2-stat"><strong>{n}</strong><span>{l}</span></div>'
        for n, l in stats
    )

def _v2_bullet_cards(sec, limit=None):
    if not sec: return ""
    bullets = sec.get("bullets") or []
    if limit: bullets = bullets[:limit]
    cards = []
    for b in bullets:
        label, body = _split_label(b)
        if label:
            cards.append(
                '<div class="svc2-mini-card reveal">'
                f'<h3>{label}</h3><p>{body}</p>'
                '</div>'
            )
        else:
            cards.append(
                '<div class="svc2-mini-card reveal">'
                f'<p>{b}</p>'
                '</div>'
            )
    return "".join(cards)

def _v2_focus_panel(sec, image, label, flip=False):
    if not sec: return ""
    paras = sec.get("paras") or []
    intro = "".join(f'<p>{p}</p>' for p in paras[:2])
    bullets = _v2_bullet_cards(sec)
    flip_cls = " flip" if flip else ""
    return (
        f'<section class="svc2-focus{flip_cls}" id="{label}">'
        '<div class="container">'
        '<div class="svc2-focus-media reveal">'
        f'<img src="{image}" alt="{_strip_tags(sec["heading"])}" loading="lazy" decoding="async">'
        '</div>'
        '<div class="svc2-focus-copy reveal">'
        f'<span class="svc2-kicker">{label.replace("-", " ")}</span>'
        f'<h2>{sec["heading"]}</h2>'
        f'<div class="svc2-prose">{intro}</div>'
        f'<div class="svc2-mini-grid">{bullets}</div>'
        '</div>'
        '</div>'
        '</section>'
    )

def _v2_process(sec):
    if not sec: return ""
    steps = []
    for i, (label, body) in enumerate(sec.get("sub") or []):
        clean = _pre_re.sub(r'^(Phase|Step|Tier|Stage|Module|Level|Track)\s+\w{1,4}\s*[—–:\-]\s*',
                       '', label, flags=_pre_re.IGNORECASE)
        steps.append(
            '<div class="svc2-process-card reveal">'
            f'<span>{(i+1):02d}</span>'
            f'<h3>{clean}</h3>'
            f'<p>{body}</p>'
            '</div>'
        )
    paras = "".join(f'<p>{p}</p>' for p in (sec.get("paras") or [])[:1])
    return (
        '<section class="svc2-process" id="process">'
        '<div class="container">'
        '<div class="svc2-section-head reveal">'
        '<span class="svc2-kicker">Process</span>'
        f'<h2>{sec["heading"]}</h2>'
        f'{paras}'
        '</div>'
        f'<div class="svc2-process-grid">{"".join(steps)}</div>'
        '</div>'
        '</section>'
    )

def _v2_industries(sec):
    if not sec: return ""
    cards = []
    for b in sec.get("bullets") or []:
        label, body = _split_label(b)
        label = label or b
        cards.append(
            '<div class="svc2-industry reveal">'
            f'<div class="svc-ind-icon">{_industry_icon(label)}</div>'
            f'<h3>{label}</h3>'
            f'{f"<p>{body}</p>" if body and body != label else ""}'
            '</div>'
        )
    return (
        '<section class="svc2-industries" id="industries">'
        '<div class="container">'
        '<div class="svc2-section-head reveal">'
        '<span class="svc2-kicker">Proof by sector</span>'
        f'<h2>{sec["heading"]}</h2>'
        '</div>'
        f'<div class="svc2-industry-grid">{"".join(cards)}</div>'
        '</div>'
        '</section>'
    )

def _v2_difference(sec):
    if not sec: return ""
    paras = "".join(f'<p>{p}</p>' for p in (sec.get("paras") or [])[:1])
    return (
        '<section class="svc2-difference" id="difference">'
        '<div class="container">'
        '<div class="svc2-section-head reveal">'
        '<span class="svc2-kicker">Why us</span>'
        f'<h2>{sec["heading"]}</h2>'
        f'{paras}'
        '</div>'
        f'<div class="svc2-diff-grid">{_v2_bullet_cards(sec)}</div>'
        '</div>'
        '</section>'
    )

def _v2_eeat(rows):
    if not rows: return ""
    cards = "".join(
        '<div class="svc2-trust-card reveal">'
        f'<span>{r["marker"]}</span>'
        f'<h3>{r["signal"]}</h3>'
        f'<p>{r["evidence"]}</p>'
        '</div>'
        for r in rows
    )
    return (
        '<section class="svc2-trust" id="trust">'
        '<div class="container">'
        '<div class="svc2-section-head reveal">'
        '<span class="svc2-kicker">E-E-A-T signals</span>'
        '<h2>Trust signals built into the work.</h2>'
        '<p>Visible proof for users and search engines: experience, expertise, authority and transparency.</p>'
        '</div>'
        f'<div class="svc2-trust-grid">{cards}</div>'
        '</div>'
        '</section>'
    )

def svc_doc_template_v2(svc):
    sections = _group_sections(svc.get("blocks") or [])
    intro_sec = sections[0] if sections and not sections[0].get("heading") else None
    process_sec = _find_section(sections, "4-phase")
    local_sec = _find_section(sections, "local seo")
    ecommerce_sec = _find_section(sections, "e-commerce seo")
    industries_sec = _find_section(sections, "industries")
    difference_sec = _find_section(sections, "different")
    intro_extra = "".join(f'<p>{p}</p>' for p in (intro_sec.get("paras") if intro_sec else [])[:2])
    faqs = svc.get("faqs") or []
    faq_html = "".join(
        f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>'
        for q, a in faqs
    )
    return (
        '<section class="svc2-hero svc2-hero-clean">'
        '<div class="container">'
        '<div class="svc2-hero-copy">'
        '<nav class="svc2-crumb">Home / Services / SEO</nav>'
        '<span class="svc2-kicker">SEO growth system</span>'
        f'<h1>{svc["h1"]}</h1>'
        f'<p>{svc["intro"]}</p>'
        '<div class="svc2-actions">'
        '<a class="btn" href="contact-us.html">Get My Free SEO Audit</a>'
        '<a class="btn-outline btn-ghost" href="#process">See The Process</a>'
        '</div>'
        '</div>'
        '<div class="svc2-hero-media reveal">'
        f'<img src="{_svc_img(svc["site_slug"])}" alt="SEO strategy and search optimisation workspace" loading="eager" decoding="async">'
        '</div>'
        '</div>'
        f'<div class="container svc2-stat-panel reveal">{_v2_stat_cards()}</div>'
        '</section>'
        '<nav class="svc2-nav" aria-label="SEO page sections">'
        '<div class="container">'
        '<a href="#overview">Overview</a><a href="#process">Process</a><a href="#local-seo">Local SEO</a><a href="#ecommerce-seo">E-Commerce</a><a href="#industries">Industries</a><a href="#trust">Trust</a><a href="#faqs">FAQs</a>'
        '</div>'
        '</nav>'
        '<section class="svc2-overview" id="overview">'
        '<div class="container">'
        '<div class="svc2-overview-copy reveal">'
        '<span class="svc2-kicker">What changes</span>'
        '<h2>Organic search becomes a revenue asset, not a reporting line.</h2>'
        f'<div class="svc2-prose">{intro_extra}</div>'
        '</div>'
        '<div class="svc2-overview-card reveal">'
        '<strong>SEO scope</strong>'
        '<span>Technical audits</span><span>Search intent strategy</span><span>Content execution</span><span>Authority building</span><span>Local visibility</span><span>E-commerce crawl systems</span>'
        '</div>'
        '</div>'
        '</section>'
        + _v2_process(process_sec)
        + _v2_focus_panel(local_sec, _svc_img("real-estate-lead-generation.html"), "local-seo")
        + _v2_focus_panel(ecommerce_sec, _svc_img("ecommerce-marketing.html"), "ecommerce-seo", flip=True)
        + _v2_industries(industries_sec)
        + _v2_difference(difference_sec)
        + _v2_eeat(svc.get("eeat_signals") or [])
        + (
            '<section class="svc2-faq" id="faqs">'
            '<div class="container">'
            '<div class="svc2-section-head reveal"><span class="svc2-kicker">FAQs</span><h2>Questions clients ask before starting SEO.</h2></div>'
            f'<div class="svc-faq-wrap">{faq_html}</div>'
            '</div>'
            '</section>' if faqs else ""
        )
        + '<section class="svc2-cta">'
        '<div class="container reveal">'
        '<h2 class="play">Ready to turn rankings into revenue?</h2>'
        '<p>Book a free SEO audit and get a prioritized roadmap for your site, keywords and growth target.</p>'
        '<a class="btn" href="contact-us.html">Start With An SEO Audit</a>'
        '</div>'
        '</section>'
    )

def svc_doc_template(svc):
    items = MARQUEE_ITEMS * 3
    marquee_html = "".join(f'<span class="marquee-item">{m}</span>' for m in items)
    title_label = SERVICE_TITLE_MAP.get(svc["site_slug"], svc["h1"])
    crumb = "Home / Services / " + title_label.replace("&amp;", "&")
    hero = (
        '<section class="about-hero svc-hero">\n'
        + HERO_ORBS
        + '  <div class="container">\n'
        + f'    <div class="breadcrumb">{crumb}</div>\n'
        + f'    <h1>{svc["h1"]}</h1>\n'
        + f'    <p class="hero-subtitle">{title_label}</p>\n'
        + f'    <p class="lead">{svc["intro"]}</p>\n'
        + '    <div class="hero-sub"><a class="btn" href="contact-us.html">Start Your Project</a></div>\n'
        + '  </div>\n</section>\n'
        + '<section class="marquee-strip" aria-hidden="true">\n'
        + f'  <div class="marquee-track">{marquee_html}</div>\n'
        + '</section>\n'
    )
    stats_html = render_stats_strip()
    eeat_html = render_eeat(svc.get("eeat_signals") or [])
    body_html = render_doc_blocks(svc.get("blocks") or [])
    faqs = svc.get("faqs") or []
    if faqs:
        items_html = "".join(
            f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>'
            for q, a in faqs
        )
        faqs_html = (
            '<section class="about-sec">\n'
            + '  <div class="container svc-faq-wrap">\n'
            + '    <div class="sec-head reveal"><span class="kicker">FAQs</span><h2>Frequently Asked <span class="green_text">Questions</span></h2></div>\n'
            + '    ' + items_html + '\n'
            + '  </div>\n</section>\n'
        )
    else:
        faqs_html = ""
    cta_html = (
        '<section class="about-cta">\n'
        '  <div class="container reveal">\n'
        '    <h2>Ready to grow your <span>brand?</span></h2>\n'
        '    <p>Book a free consultation and get a custom proposal within 48 hours.</p>\n'
        '    <a class="btn" href="contact-us.html">Start Your Project</a>\n'
        '  </div>\n</section>\n'
    )
    return hero + stats_html + eeat_html + body_html + faqs_html + cta_html

def service_jsonld(fname, title, desc, faqs=None):
    name = title.split("|")[0].strip()
    data = {
        "@context":"https://schema.org",
        "@type":"Service",
        "serviceType": name,
        "name": name,
        "description": desc,
        "provider": {"@id": SITE_URL + "/#organization"},
        "areaServed": {"@type":"Country","name":"India"},
        "url": SITE_URL + "/" + fname.replace(".html","/"),
        "offers": {"@type":"Offer","priceCurrency":"INR","availability":"https://schema.org/InStock"}
    }
    out = '<script type="application/ld+json">' + json.dumps(data, separators=(",",":")) + '</script>'
    if faqs:
        faq_data = {
            "@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[{"@type":"Question","name":_strip_tags(q),"acceptedAnswer":{"@type":"Answer","text":_strip_tags(a)}} for q,a in faqs]
        }
        out += '<script type="application/ld+json">' + json.dumps(faq_data, separators=(",",":")) + '</script>'
    return out

def _kw_for(svc):
    parts = []
    if svc.get("primary_kw"): parts.append(svc["primary_kw"].replace(" | ", ", "))
    if svc.get("secondary_kw"): parts.extend(svc["secondary_kw"])
    if svc.get("lsi_kw"): parts.extend(svc["lsi_kw"][:8])
    return DEFAULT_KEYWORDS + ", " + ", ".join(parts)

for svc in DOC_SERVICES:
    fname = svc["site_slug"]
    title = svc["meta_title"] or svc["h1"]
    desc = svc["meta_desc"] or _strip_tags(svc.get("intro",""))[:160]
    body = svc_doc_template_v2(svc) if fname == "seo.html" else svc_doc_template(svc)
    sjsonld = service_jsonld(fname, title, desc, svc.get("faqs"))
    write(fname, title, desc, body, keywords=_kw_for(svc), extra_jsonld=sjsonld)
# ---------- CASE STUDY ----------
# (slug, title, tag, description, image)
case_items = [
    ("hyundai-pledge-to-be-safe", "Hyundai &mdash; Pledge to Be Safe", "Automotive",
     "A nationwide road-safety campaign that turned a social message into 34.6M+ reach and 15.2M+ video views.",
     "assets/Case%20Studies/Pledge%20to%20Be%20Safe.webp"),
    ("khyber-cement-cementing-regional-awareness-through-digital-visibility", "Khyber Cement", "Manufacturing",
     "Cementing regional awareness across J&amp;K and North India with two TVCs &mdash; 13.9M+ impressions, 9M+ views.",
     "assets/Case%20Studies/Kypber%20Cement.webp"),
    ("jk-shah-classes-quality-leads", "JK Shah Classes &mdash; Quality Leads", "Education",
     "1,500+ leads with 80% marked high-quality via a full-funnel Meta + Google performance engine.",
     "assets/Case%20Studies/JK%20SHah%20.webp"),
    ("my-bid-app-multi-platform-growth", "MY BID App &mdash; Multi-Platform Growth", "App Growth",
     "3,400+ successful registrations across Meta, Google Search, Display and Programmatic.",
     "assets/Case%20Studies/WYBID.webp"),
    ("shiamak-one-year-program-stepping-up-digital-engagement-for-aspiring-dancers", "Shiamak &mdash; Stepping Up Digital Engagement", "Arts &amp; Education",
     "A friction-free, mobile-first system that reached aspiring dancers across 12+ cities.",
     "assets/Case%20Studies/Shamik.webp"),
    ("ebco-forging-digital-success-with-integrated-campaigns", "EBCO &mdash; Integrated Digital Success", "D2C / Industrial",
     "12M+ impressions, 100K+ clicks and 2.34x ROAS for a legacy hardware leader.",
     "assets/Case%20Studies/EBCO.webp"),
    ("hyundai-elite-i20-lead-generation-campaign", "Hyundai Elite i20 &mdash; Lead Generation", "Automotive",
     "5,000+ quality leads for the premium hatchback from 3.3M+ Meta impressions.",
     "assets/Case%20Studies/i20%20Lead%20Generation.webp"),
    ("transcon-triumph-building-leads-visibility-through-multi-platform-campaigns", "Transcon &mdash; Leads &amp; Visibility", "Real Estate",
     "289 leads + 300K+ YouTube views at a 64.08% view-through rate for a premium residential launch.",
     "assets/Case%20Studies/transcon.webp"),
    ("legal-junction-building-a-long-term-lead-engine-for-rent-agreement-services", "Legal Junction &mdash; Long-Term Lead Engine", "Legal Services",
     "450+ quality leads at 7% conversion and &#8377;450 CPL via Google Search + WhatsApp automation.",
     "assets/Case%20Studies/Legal%20Junction.webp"),
    ("seo-case-study-themauve-co", "TheMauve.co &mdash; SEO Case Study", "E-commerce &middot; SEO",
     "Technical SEO, content clusters and internal linking that lifted organic traffic for a D2C fashion brand.",
     "assets/Case%20Studies/mauve.webp"),
    ("seo-case-study-mayapuri-com", "Mayapuri.com &mdash; SEO Case Study", "Publishing &middot; SEO",
     "A structured SEO + Google Discover programme that grew non-brand organic for Bollywood news.",
     "assets/Case%20Studies/Mayapuri.webp"),
    ("case-study-gy3-fashion-sales-branding", "GY3 &mdash; Fashion, Sales &amp; Branding", "Fashion &amp; Retail",
     "PPC rebuilt as a long-term sales + branding engine &mdash; improved ROAS, stronger brand visibility.",
     "assets/Case%20Studies/GY3.webp"),
    ("ppc-case-study-tulsi-realty-9-meraki-panvel-lead-generation", "Tulsi Realty &mdash; 9 Meraki Panvel", "Real Estate &middot; PPC",
     "Geo-targeted Google Search delivering site-visit-ready homebuyers in Panvel.",
     "assets/Case%20Studies/Tusli.webp"),
    ("zedex-mobility-car-booking-campaigns", "Zedex Mobility &mdash; Car Bookings at Scale", "Automotive",
     "81 avg. bookings/month across Tata, Kia and &Scaron;koda &mdash; with up to 200X peak-season ROAS.",
     "assets/Case%20Studies/Zedex.webp"),
    ("stem-rx-regenerative-hospital-marketing", "Stem RX &mdash; Regenerative Hospital", "Healthcare",
     "&#8377;142 CPL with 90% OTP-verified lead quality and 35&ndash;45% organic growth.",
     "assets/Case%20Studies/Stem%20RX.webp"),
    ("shape-u-clinic-aesthetic-lead-generation", "Shape U Clinic &mdash; 1,556 Leads / Month", "Aesthetics",
     "A precision Meta funnel with WhatsApp automation generating 1,556 qualified treatment leads per month.",
     "assets/Case%20Studies/Shapeu.webp"),
    ("siws-school-admissions-ppc", "SIWS &mdash; Admissions Engine", "Education",
     "300 leads at &#8377;131 CPL with +65% social engagement growth for a Mumbai K&ndash;12 school.",
     "assets/Case%20Studies/Siws.webp"),
    ("rawood-sheed-timber-lead-generation", "RaWood Sheed &mdash; Niche B2B Demand", "Timber",
     "600 product inquiries/month at &#8377;50 CPI and 3X ROAS in a niche live-edge timber market.",
     "assets/Case%20Studies/The%20Rawood%20Shed.webp"),
]
case_cards = "".join(
    f'<a class="card" href="case-study-{slug}.html"><div class="thumb" style="background-image:url(\'{img}\')"></div><div class="body"><span class="tag">{tag}</span><h3>{t}</h3><p>{d}</p></div></a>'
    for (slug, t, tag, d, img) in case_items
)
cs_body = page_hero("Case <span class=\"green_text\">Studies</span>", "Home / Case Studies",
    "Real brands. Real numbers. Real growth. Explore how DigiVeritaz has helped ambitious businesses turn digital marketing into measurable revenue &mdash; across automotive, education, real estate, D2C, legal, fashion and more.") + f"""
<section><div class="container"><div class="card-grid">{case_cards}</div></div></section>

<section class="cta-band">
  <div class="container">
    <h2 class="play">Want to be our next <span class="green_text">success story?</span></h2>
    <p class="lead">Tell us about your goals &mdash; we'll build a plan with clear KPIs, timelines and accountability.</p>
    <a class="btn" href="contact-us.html">Book A Call</a>
  </div>
</section>
"""
write("case-study.html",
      "Case Studies | DigiVeritaz Digital Marketing Success Stories",
      "Explore real-world digital marketing case studies showcasing Digiveritaz growth-driven results for brands across India — lead gen, SEO and PPC wins included.",
      cs_body,
      keywords=DEFAULT_KEYWORDS + ", digital marketing case studies, marketing success stories, Hyundai case study, JK Shah case study, Mumbai agency portfolio")

# ---------- BLOG ----------
# Posts are sourced from _blog_data.json (scraped from the live WP blog).
BLOG_DATA_FILE = OUT / "_blog_data.json"
blog_data = json.loads(BLOG_DATA_FILE.read_text()) if BLOG_DATA_FILE.exists() else []

# Stock thumbnails by category for posts that don't have a featured_image.
BLOG_FALLBACK_IMG = {
    "Search Engine Optimization": "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?auto=format&fit=crop&w=1200&q=80",
    "Performance Marketing": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
    "AI-Powered Branding": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
    "Digital Marketing": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=1200&q=80",
    "SEM": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80",
}
BLOG_DEFAULT_IMG = "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=1200&q=80"

def blog_image(post):
    return post.get("featured_image") or BLOG_FALLBACK_IMG.get(post.get("category",""), BLOG_DEFAULT_IMG)

def blog_card(post):
    img = blog_image(post)
    cat = post.get("category","Insights")
    title = post["title"]
    excerpt = post.get("excerpt","")
    date_disp = post.get("date_display","")
    rt = post.get("reading_time_min")
    rt_html = f'<span class="dot"></span><span>{rt} min read</span>' if rt else ""
    return (
        f'<a class="card" href="blog-{post["slug"]}.html">'
        f'<div class="thumb" style="background-image:url(\'{img}\')"></div>'
        f'<div class="body">'
        f'<span class="tag">{cat}</span>'
        f'<h3>{title}</h3>'
        f'<p>{excerpt}</p>'
        f'<div class="meta"><span>{date_disp}</span>{rt_html}</div>'
        f'</div></a>'
    )

# ---------- BLOG LISTING ----------
blog_cards = "".join(blog_card(p) for p in blog_data) if blog_data else ""
blog_body = page_hero("Blog &amp; <span class=\"green_text\">Insights</span>", "Home / Blog",
    "Tactical playbooks, industry trends and behind-the-scenes from our team.") + f"""
<section><div class="container"><div class="card-grid">{blog_cards}</div></div></section>
"""
write("blog.html",
      "Digital Marketing Blogs and Insights | DigiVeritaz India",
      "Explore expert insights, trends and strategies on SEO, PPC, AI and performance marketing from Digiveritaz — updated weekly for brands and marketers in India.",
      blog_body,
      keywords=DEFAULT_KEYWORDS + ", digital marketing blog, SEO tips, PPC tips, marketing insights India, growth marketing blog")

# ---------- BLOG DETAIL PAGES ----------
def _twitter_share(title, url):
    import urllib.parse as _u
    q = _u.urlencode({"text": title, "url": url})
    return f"https://twitter.com/intent/tweet?{q}"
def _linkedin_share(url):
    import urllib.parse as _u
    return "https://www.linkedin.com/sharing/share-offsite/?" + _u.urlencode({"url": url})
def _facebook_share(url):
    import urllib.parse as _u
    return "https://www.facebook.com/sharer/sharer.php?" + _u.urlencode({"u": url})
def _whatsapp_share(title, url):
    import urllib.parse as _u
    return "https://wa.me/?" + _u.urlencode({"text": f"{title} {url}"})

def blog_post_body(post, related):
    slug = post["slug"]
    page_url = f"{SITE_URL}/blog-{slug}.html"
    title = post["title"]
    cat = post.get("category","Insights")
    date_disp = post.get("date_display","")
    author = post.get("author") or "DigiVeritaz"
    rt = post.get("reading_time_min")
    rt_html = f'<span class="sep"></span><span>{rt} min read</span>' if rt else ""
    img = post.get("featured_image")
    feature_html = (
        f'<section class="blog-feature"><div class="container"><img src="{img}" alt="{_strip_tags(title)}" loading="eager" decoding="async"></div></section>'
        if img else ""
    )
    body_html = post.get("body_html","")

    share_html = (
        '<div class="blog-share">'
        '<span class="lbl">Share:</span>'
        f'<a href="{_twitter_share(title, page_url)}" target="_blank" rel="noopener" aria-label="Share on Twitter"><svg viewBox="0 0 24 24"><path d="M18.9 2H22l-7.5 8.6L23.5 22h-6.9l-5.4-7-6.2 7H2l8-9.2L1.7 2h7l4.9 6.5z"/></svg></a>'
        f'<a href="{_linkedin_share(page_url)}" target="_blank" rel="noopener" aria-label="Share on LinkedIn"><svg viewBox="0 0 24 24"><path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2zM8 19H5V9h3v10zM6.5 7.7a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4zM19 19h-3v-5.3c0-1.3 0-2.9-1.8-2.9s-2 1.4-2 2.8V19h-3V9h2.9v1.4h0a3.2 3.2 0 0 1 2.9-1.6c3.1 0 3.7 2 3.7 4.7V19z"/></svg></a>'
        f'<a href="{_facebook_share(page_url)}" target="_blank" rel="noopener" aria-label="Share on Facebook"><svg viewBox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H8v-3h2.4V9.4c0-2.4 1.4-3.7 3.6-3.7 1 0 2.1.2 2.1.2v2.3h-1.2c-1.2 0-1.5.7-1.5 1.5V12h2.6l-.4 3h-2.2v7A10 10 0 0 0 22 12z"/></svg></a>'
        f'<a href="{_whatsapp_share(title, page_url)}" target="_blank" rel="noopener" aria-label="Share on WhatsApp"><svg viewBox="0 0 24 24"><path d="M20.5 3.5A11.4 11.4 0 0 0 12 0C5.5 0 .2 5.3.2 11.8c0 2.1.5 4.1 1.6 5.9L0 24l6.4-1.7c1.7.9 3.6 1.4 5.6 1.4 6.5 0 11.8-5.3 11.8-11.8 0-3.2-1.2-6.1-3.3-8.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4a9.7 9.7 0 0 1-1.5-5.4C2.2 6.4 6.6 2 12 2s9.8 4.4 9.8 9.8-4.4 10-9.8 10z"/></svg></a>'
        '</div>'
    )

    related_html = ""
    if related:
        cards = "".join(blog_card(r) for r in related)
        related_html = f"""
<section class="blog-related">
  <div class="container">
    <h2 class="play">Related <span class="green_text">reads</span></h2>
    <div class="card-grid">{cards}</div>
  </div>
</section>
"""

    return f"""
<section class="blog-hero">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> &rsaquo;
      <a href="blog.html">Blog</a> &rsaquo;
      <span>{_strip_tags(title)[:60]}</span>
    </nav>
    <span class="post-tag">{cat}</span>
    <h1 class="play">{title}</h1>
    <div class="post-meta">
      <span>By {author}</span>
      <span class="sep"></span>
      <span>{date_disp}</span>
      {rt_html}
    </div>
  </div>
</section>
{feature_html}
<section class="blog-article">
  <div class="container">
    <article class="prose">
      {body_html}
    </article>
    {share_html}
  </div>
</section>
{related_html}
<section class="cta-band">
  <div class="container">
    <h2 class="play">Want results like <span class="green_text">these?</span></h2>
    <p class="lead">Let's turn insights into measurable growth. Book a free strategy call with the DigiVeritaz team.</p>
    <a class="btn" href="contact-us.html">Book A Call</a>
  </div>
</section>
"""

def blog_jsonld(post):
    img = post.get("featured_image") or DEFAULT_OG_IMAGE
    page_url = f"{SITE_URL}/blog-{post['slug']}.html"
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "headline": _strip_tags(post["title"])[:110],
        "description": post.get("excerpt",""),
        "image": img,
        "datePublished": post["date"],
        "dateModified": post["date"],
        "author": {"@type": "Organization", "name": post.get("author") or "DigiVeritaz", "url": SITE_URL},
        "publisher": {"@id": SITE_URL + "/#organization"},
        "articleSection": post.get("category",""),
        "inLanguage": "en-IN",
    }
    crumbs = {
        "@context":"https://schema.org","@type":"BreadcrumbList",
        "itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":SITE_URL+"/"},
            {"@type":"ListItem","position":2,"name":"Blog","item":SITE_URL+"/blog.html"},
            {"@type":"ListItem","position":3,"name":_strip_tags(post["title"])[:80],"item":page_url},
        ]
    }
    return ('<script type="application/ld+json">' + json.dumps(data, separators=(",",":")) + '</script>'
            + '<script type="application/ld+json">' + json.dumps(crumbs, separators=(",",":")) + '</script>')

BLOG_KEYWORDS_BY_CAT = {
    "Search Engine Optimization": "SEO blog India, SEO tips, technical SEO, local SEO, keyword research, organic growth",
    "Performance Marketing": "performance marketing blog, ROAS optimization, CAC reduction, paid media insights",
    "AI-Powered Branding": "AI marketing, generative search optimization, ChatGPT marketing, AI branding",
    "Digital Marketing": "digital marketing blog India, online marketing tips, multi-channel marketing",
    "SEM": "search engine marketing, SEM blog, Google Ads insights, paid search strategy",
}

for i, post in enumerate(blog_data):
    # Pick up to 3 related posts: same category first, fall back to others.
    same_cat = [p for j, p in enumerate(blog_data) if j != i and p.get("category") == post.get("category")]
    others = [p for j, p in enumerate(blog_data) if j != i and p.get("category") != post.get("category")]
    related = (same_cat + others)[:3]
    body = blog_post_body(post, related)
    cat = post.get("category","")
    kw = DEFAULT_KEYWORDS + ", " + BLOG_KEYWORDS_BY_CAT.get(cat, "digital marketing blog")
    desc = post.get("excerpt") or _strip_tags(post["title"])
    write(
        f"blog-{post['slug']}.html",
        f"{post['title']} | DigiVeritaz",
        desc,
        body,
        keywords=kw,
        extra_jsonld=blog_jsonld(post),
    )

# ---------- FAQ ----------
faqs = [
    ("Do you guarantee results?", "We operate on a performance-first model and align every engagement with clear KPIs — CPA, ROAS, LTV, or qualified leads — depending on your business stage. While no agency can ethically guarantee outcomes, our contracts are built around measurable milestones we commit to."),
    ("What kind of businesses do you work with?", "Startups, SMEs and enterprise brands across education, real estate, automotive, D2C, retail, F&amp;B, BFSI and services. If you have a growth target and a real product, we can probably help."),
    ("How do AI tools and automation fit into your work?", "We integrate best-in-class platforms like AIsensy (WhatsApp), SE Ranking (SEO), Zapier (automation), and custom GPT workflows to reduce manual effort and increase decision speed."),
    ("Do you offer branding and design services?", "Yes — we run a full-service creative team covering brand strategy, identity systems, content, and campaign creative. It's fully integrated with our performance work."),
    ("Can you handle lead-gen AND e-commerce?", "Absolutely. Our team runs both full-funnel lead-gen engines and e-commerce growth programs across Amazon, Flipkart, Shopify and D2C stores."),
    ("How do you measure success and ROI?", "Transparent dashboards tracking CPA, ROAS, LTV, pipeline velocity and business metrics — not vanity numbers. We share reports weekly and run strategic reviews monthly."),
    ("How involved do I need to be?", "Flexible. Some clients prefer weekly strategy calls; others want a hands-off, turnkey engagement. We adapt to your working style."),
    ("Do you offer ongoing support?", "Yes — both retainer and project-based engagements. Most clients stay 12+ months because of the results."),
    ("How do we get started?", "Book a discovery call, share your goals and current state, and we'll come back with a custom strategy and proposal within a few days."),
    ("Where are you based?", "Our HQ is in Chembur, Mumbai (Deonar), and we work with clients across India and overseas."),
]
faq_html = "".join(f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>' for q,a in faqs)
faq_body = page_hero("Frequently Asked <span class=\"green_text\">Questions</span>", "Home / FAQ",
    "Everything you wanted to know about working with DigiVeritaz.") + f"""
<section><div class="container" style="max-width:820px">{faq_html}</div></section>
"""
import re as _re
def _strip_tags(s): return _re.sub(r'<[^>]+>','',s).replace('&amp;','&').strip()
faq_schema = {
    "@context":"https://schema.org","@type":"FAQPage",
    "mainEntity":[{
        "@type":"Question","name":_strip_tags(q),
        "acceptedAnswer":{"@type":"Answer","text":_strip_tags(a)}
    } for q,a in faqs]
}
faq_jsonld = '<script type="application/ld+json">' + json.dumps(faq_schema, separators=(",",":")) + '</script>'
write("faq.html",
      "Frequently Asked Questions (FAQ's) | Digiveritaz India",
      "Find answers to common questions about Digiveritaz digital marketing, SEO and performance marketing services for businesses and brands across all of India.",
      faq_body,
      keywords=DEFAULT_KEYWORDS + ", digital marketing FAQ, marketing agency questions, marketing pricing, ROI measurement",
      extra_jsonld=faq_jsonld)

# ---------- PRIVACY ----------
privacy_body = page_hero("Privacy <span class=\"green_text\">Policy</span>", "Home / Privacy Policy", "") + """
<section><div class="container prose" style="max-width:820px">
<p><em>Last updated: April 2026</em></p>
<h2>1. Introduction</h2><p>DigiVeritaz ("we", "our", "us") respects your privacy. This policy explains how we collect, use and protect information you share with us.</p>
<h2>2. Consent</h2><p>By using our website or services, you consent to the collection and use of information in accordance with this policy.</p>
<h2>3. Information We Collect</h2><p>We may collect your name, email, phone number, company, budget, and project details when you fill out a form or contact us directly.</p>
<h2>4. How We Use Information</h2><p>Information is used only to respond to your inquiry, deliver services, send updates you've opted into, and improve our offerings.</p>
<h2>5. Data Retention</h2><p>We retain your data only as long as necessary for the purposes outlined in this policy, or as required by law.</p>
<h2>6. Your Rights</h2><p>You may request access to, correction of, or deletion of your personal data at any time by emailing durvamukherjee@digiveritaz.com.</p>
<h2>7. Data Sharing</h2><p>We do not sell your data. We share it only with trusted service providers who help us operate our business, under strict confidentiality.</p>
<h2>8. Security</h2><p>We implement industry-standard safeguards to protect your data, though no method of transmission over the Internet is 100% secure.</p>
<h2>9. External Links</h2><p>Our site may contain links to external sites whose privacy practices we do not control.</p>
<h2>10. Marketing Opt-Out</h2><p>You can opt out of marketing communications at any time by using the unsubscribe link in our emails.</p>
<h2>11. Contact</h2><p>Privacy Officer: Durva Mukherjee · durvamukherjee@digiveritaz.com · +91 99566 55662 · Ujagar Chambers, Deonar, Chembur, Mumbai, Maharashtra 400088.</p>
<h2>12. Updates</h2><p>We may update this policy from time to time. Material changes will be communicated via our website.</p>
</div></section>
"""
write("privacy-policy.html",
      "Privacy Policy | Digiveritaz Digital Marketing India",
      "Read Digiveritaz privacy policy to understand how we collect, use and protect your personal and business data responsibly across all operations in India.",
      privacy_body,
      keywords="privacy policy, data protection, DigiVeritaz privacy")

# ---------- TERMS ----------
terms_body = page_hero("Terms &amp; <span class=\"green_text\">Conditions</span>", "Home / Terms", "") + """
<section><div class="container prose" style="max-width:820px">
<h2>1. Introduction</h2><p>These Terms and Conditions govern your use of DigiVeritaz services. By engaging with us, you agree to these terms.</p>
<h2>2. Payments, Billing &amp; Taxes</h2><p>Fees are billed monthly unless otherwise agreed. Late payments attract 18% annual interest. All applicable taxes are charged extra.</p>
<h2>3. Subscription &amp; Renewal</h2><p>Retainers do not auto-renew. Engagements are reviewed at least one month before expiration to agree on next-term scope and pricing.</p>
<h2>4. Client Responsibilities</h2><p>You agree to provide timely access, approvals and information required for us to deliver services. Delays caused by the client may impact timelines.</p>
<h2>5. Confidentiality</h2><p>Both parties agree to keep confidential information shared during the engagement strictly confidential, during and after the engagement.</p>
<h2>6. Termination</h2><p>Either party may terminate with 30 days' written notice. Fees for work already delivered remain payable.</p>
</div></section>
"""
write("terms-and-conditions.html",
      "Terms &amp; Conditions | Digiveritaz Digital Marketing India",
      "Review the terms and conditions governing the use of Digiveritaz website, services and digital marketing solutions for businesses and brands across India.",
      terms_body,
      keywords="terms and conditions, service agreement, DigiVeritaz terms")

print("Built pages:")
for f in sorted(OUT.glob("*.html")):
    print(" -", f.name)
