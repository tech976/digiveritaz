#!/usr/bin/env python3
"""Static page builder for DigiVeritaz recreation.
Generates all HTML pages from shared header/footer + per-page content blocks.
"""
import os, pathlib

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

SERVICES_DROPDOWN = [
    ("services.html", "All Services"),
    ("organic-marketing-services.html", "Organic Marketing Services"),
    ("paid-social-media-advertising.html", "Paid Social Media Advertising"),
    ("pay-per-click.html", "Pay Per Click"),
    ("performance-marketing-agency.html", "Performance Marketing Agency"),
    ("ecommerce-marketing.html", "E-Commerce Platforms"),
    ("data-strategy-consulting-services.html", "Data Strategy &amp; Consulting"),
    ("native-advertising.html", "Native Advertising"),
    ("whatsapp-marketing-services.html", "WhatsApp Marketing Services"),
    ("branding-and-design.html", "Branding and Design"),
    ("seo.html", "Search Engine Optimization"),
    ("generative-search-optimisation.html", "Generative Search Optimisation"),
]

SERVICE_SLUGS = {"seo.html","pay-per-click.html","performance-marketing-agency.html","paid-social-media-advertising.html","ecommerce-marketing.html","whatsapp-marketing-services.html","native-advertising.html","organic-marketing-services.html","branding-and-design.html","generative-search-optimisation.html","data-strategy-consulting-services.html","services.html"}

def build_nav(current):
    def is_active(href):
        if href == current: return True
        if href == "services.html" and current in SERVICE_SLUGS:
            return True
        return False

    def dropdown_html():
        items = "".join(
            f'<a href="{h}"{" class=\"active\"" if h == current else ""}>{label}</a>'
            for h, label in SERVICES_DROPDOWN
        )
        return f'<div class="dd-menu" role="menu"><span class="dd-bridge" aria-hidden="true"></span>{items}</div>'

    lis_parts = []
    for h, t, k in NAV_ITEMS:
        active_cls = " active" if is_active(h) else ""
        if h == "services.html":
            lis_parts.append(
                f'<li class="has-dd"><a class="navlink{active_cls}" href="{h}" data-i18n="{k}">{t} <span class="dd-caret" aria-hidden="true">▾</span></a>{dropdown_html()}</li>'
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
DEFAULT_OG_IMAGE = "https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp"

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
            "email": "info@digiveritaz.com",
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
<meta property="og:image" content="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp">
<meta property="og:image:alt" content="DigiVeritaz — Digital Marketing Agency">
<meta property="og:locale" content="en_IN">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@digiveritaz">
<meta name="twitter:creator" content="@digiveritaz">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp">

<!-- Favicon -->
<link rel="icon" type="image/webp" href="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp">
<link rel="apple-touch-icon" href="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp">

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
      <img src="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp" alt="DigiVeritaz">
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
            <img src="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp" alt="DigiVeritaz">
            <span class="wordmark"><b>Digi</b>Veritaz</span>
          </a>
          <p class="foot-tag">Mumbai-based digital marketing agency helping brands across India achieve measurable ROI through SEO, paid media, and performance marketing.</p>
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
            <div><strong>Mumbai HQ</strong><a href="https://maps.google.com/?q=Ujagar+Chambers+Deonar+Chembur+Mumbai+400088" target="_blank" rel="noopener">1st Floor, Ujagar Chambers, Bus Depot, Sion&ndash;Trombay Rd, opp. Deonar, Chembur, Mumbai 400088</a></div>
          </div>
          <div class="foot-contact-row">
            <span class="ic"><svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2z"/></svg></span>
            <div><strong>Phone</strong><a href="tel:+919956655662">+91 99566 55662</a><br><a href="tel:+917021450830">+91 70214 50830</a><br><a href="tel:+917045337060">+91 70453 37060</a></div>
          </div>
          <div class="foot-contact-row">
            <span class="ic"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg></span>
            <div><strong>Email</strong><a href="mailto:info@digiveritaz.com">info@digiveritaz.com</a><br><a href="mailto:mihir@digiveritaz.com">mihir@digiveritaz.com</a></div>
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
          <span class="mv-deco" aria-hidden="true">
            <svg viewBox="0 0 240 170">
              <path d="M28 120 C 24 96, 28 78, 44 70 C 54 64, 68 62, 80 66 C 86 60, 96 58, 106 62 C 116 66, 120 74, 118 84 M 122 84 C 122 74, 130 66, 142 62 C 154 58, 168 60, 178 68 C 196 76, 202 96, 198 118 C 194 138, 178 148, 160 144 C 140 138, 128 120, 124 104"/>
              <circle cx="82" cy="104" r="22"/>
              <circle cx="82" cy="104" r="10"/>
              <circle cx="158" cy="104" r="22"/>
              <circle cx="158" cy="104" r="10"/>
              <path d="M104 104 L136 104"/>
              <path d="M40 130 L 50 152 M 200 130 L 190 152"/>
            </svg>
          </span>
          <h3>Our Vision</h3>
          <p>To become a <strong>global benchmark in performance marketing</strong> by blending time-tested expertise, disruptive innovation, and data-driven intelligence — transforming how brands grow, engage, and convert in the digital age.</p>
        </div>
        <div class="mv-card mv-mission">
          <span class="mv-deco" aria-hidden="true">
            <svg viewBox="0 0 220 200">
              <ellipse cx="110" cy="150" rx="82" ry="16"/>
              <path d="M110 148 L110 92 L150 72 L150 128 Z"/>
              <path d="M110 148 L70 128 L70 72 L110 92 Z"/>
              <path d="M150 72 L110 92 L70 72"/>
              <circle cx="110" cy="108" r="6"/>
              <circle cx="110" cy="108" r="14"/>
              <circle cx="110" cy="108" r="22"/>
              <path d="M60 40 L104 100 M50 56 L98 108 M70 26 L112 96"/>
              <path d="M56 42 L60 52 L68 48 Z M46 58 L50 68 L58 64 Z M66 28 L70 38 L78 34 Z"/>
              <path d="M110 164 L96 188 M110 164 L124 188 M96 188 L124 188"/>
            </svg>
          </span>
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
      "About DigiVeritaz | Growth-Driven Digital Marketing Agency in Mumbai",
      "DigiVeritaz is a performance marketing powerhouse based in Mumbai — 60+ clients, 15+ years combined experience, 1.15L+ leads delivered and 4–10x ROAS across India and globally.",
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
        <span class="sv-sub"><a href="tel:+917021450830">+91 70214 50830</a> &middot; <a href="tel:+917045337060">+91 70453 37060</a></span>
      </div>

      <div class="strip-item">
        <span class="sl">Email</span>
        <a class="sv" href="mailto:info@digiveritaz.com">info@digiveritaz.com</a>
        <span class="sv-sub"><a href="mailto:mihir@digiveritaz.com">mihir@digiveritaz.com</a></span>
      </div>

      <div class="strip-item">
        <span class="sl">Office</span>
        <a class="sv" href="https://maps.google.com/?q=Ujagar+Chambers+Deonar+Chembur+Mumbai+400088" target="_blank" rel="noopener">1st Floor, Ujagar Chambers</a>
        <span class="sv-sub">Bus Depot, Sion&ndash;Trombay Rd, opp. Deonar, Chembur, Mumbai 400088<br>Mon&ndash;Sat &middot; 10:00 AM &ndash; 7:00 PM</span>
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
      "Contact DigiVeritaz | Get a Free Digital Marketing Proposal",
      "Contact DigiVeritaz for a free digital marketing proposal. Call +91 99566 55662 or email info@digiveritaz.com. Based in Mumbai, serving clients across India and globally.",
      contact_body,
      keywords=DEFAULT_KEYWORDS + ", contact digital marketing agency, marketing agency Mumbai contact, free marketing proposal, digital marketing consultation",
      extra_jsonld=contact_jsonld)

# ---------- THANK YOU ----------
ty_body = """<section class="hero"><div class="container text-center">
<h1 class="play">Thank <span class="green_text">You!</span></h1>
<p class="lead" style="margin:0 auto">We've received your message and will get back to you shortly. If your inquiry is urgent, please call us directly at <a href="tel:+919956655662">+91 99566 55662</a>, <a href="tel:+917021450830">+91 70214 50830</a> or <a href="tel:+917045337060">+91 70453 37060</a>.</p>
<div class="mt-20"><a class="btn" href="index.html">Back to Home</a></div>
</div></section>"""
write("thank-you.html", "Thank You | DigiVeritaz",
      "Thank you for contacting DigiVeritaz. We'll respond within one business day.",
      ty_body)

# ---------- SERVICES HUB ----------
ICON = {
    "seo":       '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    "ppc":       '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "perf":      '<svg viewBox="0 0 24 24"><path d="M3 20h18"/><rect x="5" y="12" width="3" height="7" rx="1"/><rect x="11" y="8" width="3" height="11" rx="1"/><rect x="17" y="4" width="3" height="15" rx="1"/></svg>',
    "social":    '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="3"/><circle cx="12" cy="12" r="3.5"/><circle cx="17" cy="7" r="1"/></svg>',
    "ecom":      '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg>',
    "whatsapp":  '<svg viewBox="0 0 24 24"><path d="M4 11a8 8 0 1 1 3.5 6.6L3 19l1.4-4.2A7.9 7.9 0 0 1 4 11z"/></svg>',
    "native":    '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/><circle cx="7" cy="7.5" r="0.7"/></svg>',
    "organic":   '<svg viewBox="0 0 24 24"><path d="M12 21c5-4 9-9 9-14 0-2-1-3-3-3-3 0-4 3-6 3s-3-3-6-3c-2 0-3 1-3 3 0 5 4 10 9 14z"/></svg>',
    "brand":     '<svg viewBox="0 0 24 24"><path d="M9 3l3 5 5 1-4 4 1 6-5-3-5 3 1-6-4-4 5-1z"/></svg>',
    "ai":        '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="3"/><circle cx="9" cy="12" r="1.2"/><circle cx="15" cy="12" r="1.2"/><path d="M12 5V2"/><path d="M2 12h2M20 12h2"/></svg>',
    "data":      '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>',
}
services_list = [
    ("SEO", "seo.html", ICON["seo"], "Rank, engage, and grow sustainably with on-page, technical and content SEO."),
    ("Pay Per Click", "pay-per-click.html", ICON["ppc"], "High-intent traffic through Google Ads, Bing Ads and performance PPC campaigns."),
    ("Performance Marketing", "performance-marketing-agency.html", ICON["perf"], "Full-funnel growth through measurable, ROI-first campaigns."),
    ("Paid Social Advertising", "paid-social-media-advertising.html", ICON["social"], "Meta, LinkedIn, Pinterest and Snapchat ads that convert."),
    ("E-Commerce Marketing", "ecommerce-marketing.html", ICON["ecom"], "Amazon, Flipkart and D2C growth from listing to loyalty."),
    ("WhatsApp Marketing", "whatsapp-marketing-services.html", ICON["whatsapp"], "Conversational commerce that drives direct response."),
    ("Native Advertising", "native-advertising.html", ICON["native"], "Reach users where they read — premium native placements."),
    ("Organic Marketing", "organic-marketing-services.html", ICON["organic"], "Long-term organic growth across search, social and content."),
    ("Branding &amp; Design", "branding-and-design.html", ICON["brand"], "Research-led branding, identity systems and creative direction."),
    ("Generative Search Optimisation", "generative-search-optimisation.html", ICON["ai"], "Get discovered in ChatGPT, Gemini and AI search."),
    ("Data Strategy &amp; Consulting", "data-strategy-consulting-services.html", ICON["data"], "Attribution, analytics and a data stack that drives decisions."),
]
svc_cards = "\n".join(
    f'<div class="svc-card"><div class="icon">{i}</div><h3>{t}</h3><p>{d}</p><a class="more" href="{u}">Learn more →</a></div>'
    for (t,u,i,d) in services_list
)
svc_body = page_hero("Our <span class=\"green_text\">Services</span>", "Home / Services",
    "A full-stack suite of digital marketing services — pick one, or let us run your entire growth engine.") + f"""
<section class="services"><div class="container"><div class="services-grid">{svc_cards}</div></div></section>
"""
write("services.html",
      "Digital Marketing Services in India | SEO, PPC, Performance, E-Commerce | DigiVeritaz",
      "Full-stack digital marketing services from DigiVeritaz: SEO, PPC, performance marketing, paid social, e-commerce, WhatsApp marketing, branding, data strategy and generative search optimization.",
      svc_body,
      keywords=DEFAULT_KEYWORDS + ", digital marketing services, marketing services India, full service marketing agency, marketing packages Mumbai")

# ---------- INDIVIDUAL SERVICE PAGES ----------
service_pages = {
    "seo.html": {
        "title": "SEO Services in India | Sustainable Organic Growth | DigiVeritaz",
        "desc": "Performance-driven SEO company in India — technical audits, content strategy, ethical link building and localized targeting that cuts ad dependency and grows long-term organic revenue.",
        "h1": "SEO Company in India That Powers <span class=\"green_text\">Sustainable Growth</span>",
        "crumb": "Home / Services / SEO",
        "kicker": "Search Engine Optimization",
        "intro": "We're a performance-driven SEO company helping businesses cut ad dependency and achieve long-term organic growth — with proven expertise across industries and transparent reporting on every metric that matters.",
        "benefits": [
            ("ROI-Focused Approach", "Qualified leads over vanity traffic — every tactic tied to revenue."),
            ("Industry-Proven Expertise", "Campaigns across startups, SMEs, and enterprises with measurable results."),
            ("Technical Precision", "Core Web Vitals fixes, structured data and crawl efficiency baked in."),
            ("Ethical Link Building", "High-authority backlinks via genuine outreach — no black-hat shortcuts."),
            ("Localized Targeting", "Geo-optimized content and GMB strategy that wins local intent."),
            ("Transparent Reporting", "Monthly dashboards with business KPIs, not vanity numbers."),
        ],
        "deliverables": [
            "On-Page SEO (keyword mapping, meta optimization, content alignment)",
            "Technical SEO (speed, structured data, crawl efficiency)",
            "Off-Page &amp; Authority Building (ethical link outreach)",
            "Local SEO (GMB optimization, reviews strategy)",
            "E-Commerce SEO (product &amp; category rankings)",
            "Enterprise SEO (scalable strategies for complex sites)",
        ],
        "process": [
            ("Comprehensive Audit", "We identify visibility gaps, site-health issues and competitor benchmarks."),
            ("Strategy Development", "A tailored SEO roadmap aligned with your business goals and priorities."),
            ("On-Page &amp; Technical Execution", "Ranking improvements, structured data and content alignment shipped."),
            ("Off-Page &amp; Authority Building", "Genuine outreach to build durable trust signals and citations."),
            ("Performance Tracking", "Transparent monthly reports with growth insights and next actions."),
        ],
        "faqs": [
            ("How long does it take to see SEO results?", "Typically 3–6 months depending on your website's current state, domain authority and industry competition. Foundational wins often appear in weeks, while ranking consolidation takes longer."),
            ("Do you handle international or multilingual SEO?", "Yes — we specialize in multilingual and international SEO strategies including hreflang, regional content, and geo-specific link profiles."),
            ("What makes your SEO approach different?", "We combine technical precision, content excellence and transparent reporting to deliver results that impact your bottom line — not just Search Console charts."),
        ],
    },
    "organic-marketing-services.html": {
        "title": "Organic Marketing Services | Sustainable Growth Without Paid Ads | DigiVeritaz",
        "desc": "Drive sustainable growth without paid ads. SEO, content marketing, social media optimization and data-driven strategies that build long-term visibility, trust and traffic that converts.",
        "h1": "Organic Marketing <span class=\"green_text\">Services</span>",
        "crumb": "Home / Services / Organic Marketing",
        "kicker": "Drive Sustainable Growth Without Paid Ads",
        "intro": "At DigiVeritaz, our <strong>organic marketing services</strong> help your brand grow naturally — without depending solely on paid ads. We use SEO, content marketing, social media optimization, and data-driven strategies to build long-term visibility, trust, and traffic that converts. Whether you're a startup, small business, or enterprise, our <strong>organic marketing agency in India</strong> focuses on one goal — helping your brand attract the right audience consistently.",
        "highlights": [
            {
                "heading": "What Is <span class=\"green_text\">Organic Marketing?</span>",
                "body1": "Organic marketing is the art of growing your business using <strong>non-paid, strategic channels</strong> such as search engines, social media, blogs, and community engagement.",
                "body2": "Unlike paid ads that disappear when the budget stops, organic marketing builds lasting visibility. It involves optimizing your online presence, creating valuable content, and engaging authentically with your audience to gain trust, awareness, and loyalty.",
                "body3": "<em>In short: paid marketing brings traffic; organic marketing builds relationships that last.</em>",
                "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
                "side": "right",
            },
        ],
        "sub_services": [
            ("seo", "Organic SEO (Search Engine Optimization)", "We help your website rank higher on Google using ethical SEO practices. From keyword research and on-page optimization to backlink building, we ensure your site gains organic visibility and sustainable traffic over time."),
            ("content", "Content Marketing for Organic Growth", "Quality content is at the heart of every successful organic campaign. We create SEO-optimized blogs, website content, infographics, and videos that educate, engage, and convert. Our team focuses on content marketing for organic growth — designed to attract users and boost brand authority."),
            ("social", "Social Media Organic Marketing", "We craft organic social media strategies that increase your brand's reach without heavy ad spend. Our approach involves consistent posting, storytelling, engagement, and community building."),
            ("lead", "Organic Lead Generation", "Through optimized funnels, SEO content, and engagement strategies, we help you generate qualified leads organically. No spam, no bots — just real people interested in your brand."),
            ("video", "YouTube &amp; Video Organic Marketing", "We optimize your YouTube and video content for search visibility — ensuring you get organic traffic and engagement. From keyword tagging to compelling descriptions, every detail is optimized."),
        ],
        # "Why Choose" as split panel with bullets + CTA
        "highlight": {
            "heading": "Why Choose DigiVeritaz For <span class=\"green_text\">Organic Marketing?</span>",
            "intro": "Choosing the right organic marketing agency can be the difference between short-term hype and long-term success.<br><br><strong>Here's what makes us different:</strong>",
            "bullets": [
                ("Data-Driven Strategy", "Every campaign starts with deep analytics and market research."),
                ("Ethical SEO Practices", "100% white-hat, no shortcuts — only sustainable growth."),
                ("Personalized Campaigns", "Tailored to your business goals and audience intent."),
                ("Integrated Content &amp; SEO", "Our team aligns content, keywords, and strategy to maximize organic reach."),
                ("Proven Results", "Our clients have seen up to <strong>5× organic traffic growth</strong> within months."),
            ],
            "img": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=900&q=80",
            "side": "left",
            "cta_text": "Launch Your Brand With Us",
        },
        "process": [
            ("Audit &amp; Strategy Building", "We evaluate your website, content and competition to shape the plan."),
            ("Keyword Mapping &amp; Content Planning", "Identify <strong>high-volume, low-difficulty keywords</strong> to rank faster."),
            ("On-Page SEO Optimization", "Improve meta tags, content structure and user experience."),
            ("Content Creation &amp; Distribution", "Create valuable blogs, landing pages and social posts."),
            ("Engagement &amp; Outreach", "Build trust and backlinks through organic engagement."),
            ("Tracking &amp; Reporting", "Monitor analytics to measure traffic, leads and ROI."),
        ],
        "simple_benefits": {
            "heading": "Benefits of <span class=\"green_text\">Organic Marketing</span>",
            "items": [
                "<strong>Builds long-term trust</strong> &amp; brand authority",
                "<strong>Saves cost</strong> vs paid ads",
                "Drives <strong>consistent website traffic</strong>",
                "Improves <strong>SEO rankings</strong> &amp; visibility",
                "Generates <strong>quality organic leads</strong>",
                "Enhances <strong>audience loyalty</strong>",
            ],
        },
        "industries": ["E-commerce &amp; Retail", "Real Estate", "Education &amp; EdTech", "Healthcare &amp; Wellness", "Finance &amp; Insurance", "Technology &amp; SaaS"],
        "cta": ("Ready to Grow <span>Organically?</span>", "Let's build your brand presence the right way — naturally, strategically, and sustainably. Contact DigiVeritaz today to discuss your organic marketing strategy."),
        "faqs": [
            ("How is organic marketing different from paid marketing?", "Paid marketing buys visibility — the moment spend stops, traffic stops. Organic marketing builds assets (rankings, content, communities) that keep working long after the initial investment. Paid is rented attention; organic is owned attention."),
            ("How long before I see results from organic marketing?", "You'll see early signals — rankings improvements, traffic lifts, engagement — within 2–3 months. Meaningful compounding growth typically shows in months 4–6. Our clients have seen up to 5× organic traffic growth within that window."),
            ("Do I still need paid ads if I invest in organic?", "Not necessarily, but the two work best together. Paid can validate messaging fast; organic compounds cheaply over time. We often start with both, then shift budget toward whichever channel wins on unit economics."),
            ("What's included in your organic marketing retainer?", "Audits, keyword &amp; content strategy, on-page SEO, content production, organic social, link building outreach, analytics dashboards and monthly reviews — all tied to business KPIs, not vanity metrics."),
            ("Will organic marketing work for my industry?", "Almost always — but approach and timelines differ. E-commerce, SaaS, local services and B2B all respond to organic, though intent and content formats vary. We tailor the plan to your specific vertical and competitors."),
            ("Do you follow white-hat SEO practices?", "Yes — 100%. No PBNs, no link farms, no cloaking. Only editorial links, quality content and technical fundamentals. Google penalties are not a risk worth taking with your brand."),
        ],
    },
    "paid-social-media-advertising.html": {
        "title": "Paid Social Media Advertising | Meta, LinkedIn, YouTube Ads | DigiVeritaz",
        "desc": "Paid social media advertising that drives real ROI. Facebook, Instagram, LinkedIn and YouTube campaigns blending video-led creative with precise targeting and retargeting funnels.",
        "h1": "Paid Social Media <span class=\"green_text\">Advertising</span>",
        "crumb": "Home / Services / Paid Social",
        "kicker": "Paid Social Advertising",
        "intro": "In today's competitive landscape, organic reach alone isn't enough to keep your brand visible. <strong>Paid advertising on social media</strong> allows you to connect with the right audience, at the right time, with precision targeting. At DigiVeritaz, our <strong>paid social media agency</strong> team designs impactful <strong>social media campaigns</strong> that not only build awareness but also generate measurable business outcomes.",
        "highlight": {
            "heading": "Why Paid Social Media Advertising <span class=\"green_text\">Matters?</span>",
            "body": "Every brand wants to stand out on platforms like Facebook, Instagram, LinkedIn, and YouTube. But with constant content overload, only the right <strong>social ad campaigns</strong> can capture attention. Paid campaigns give your business the edge to break through the clutter. From building trust to driving conversions, <strong>social media digital marketing</strong> is the fastest way to amplify your presence and scale results.",
            "img": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=900&q=80",
            "cta_text": "Launch Your Brand With Us",
            "side": "right",
        },
        "approach": {
            "heading": "Our Approach To Social Media <span class=\"green_text\">Ad Campaigns</span>",
            "body1": "We believe effective campaigns come from a mix of strategy, creativity, and continuous optimization. Before launching any campaign, our team dives deep into audience research and business goals. This ensures that your ads speak directly to the people who matter most.",
            "body2": "Once strategy is set, we create compelling ad creatives—often video-led—that stop the scroll and inspire action. Every campaign is monitored closely, with regular adjustments in targeting, bidding, and creatives to ensure maximum ROI. This full-funnel approach makes our <strong>social media campaigns</strong> both impactful and cost-efficient.",
            "img": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=900&q=80",
            "side": "left",
        },
        "platforms_intro": "Our expertise covers a wide range of platforms, allowing us to design <strong>the best social media ad campaigns</strong> tailored to each business.",
        "platforms": [
            ("fb", "Facebook &amp; Instagram Ads", "Ideal for mass awareness and targeted engagement across Meta's ecosystem."),
            ("ln", "LinkedIn Ads", "Perfect for B2B brands looking to generate high-quality leads at scale."),
            ("yt", "YouTube &amp; Video Ads", "Great for storytelling and building a stronger emotional connection with your audience."),
        ],
        "platforms_outro": "No matter the platform, we ensure your message reaches the right audience in the most effective way.",
        "benefits_intro": "Investing in <strong>paid advertising social media</strong> campaigns gives your brand an edge over competitors. Unlike organic marketing, these campaigns are targeted, measurable, and scalable. Partnering with the right <strong>paid social media agency</strong> ensures that your investment translates into real business growth.",
        "benefits": [
            ("Wider Reach &amp; Visibility", "Your ads are shown to people who fit your ideal customer profile, boosting awareness beyond your existing followers.", "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80"),
            ("Faster Results", "While organic posts take time, <strong>social ad campaigns</strong> generate quick traffic, leads, and sales.", "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?auto=format&fit=crop&w=800&q=80"),
            ("Precise Targeting", "Ads can be targeted based on location, demographics, interests, and behaviors — ensuring your spend reaches the right audience.", "https://images.unsplash.com/photo-1553484771-371a605b060b?auto=format&fit=crop&w=800&q=80"),
            ("Budget Flexibility", "Start with a small budget and scale up once you see results — making it cost-effective for all business sizes.", "https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=800&q=80"),
            ("Better Brand Awareness", "Consistent exposure through <strong>social media campaigns</strong> builds trust and recognition in the minds of your audience.", "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=800&q=80"),
            ("Higher Engagement", "Creative formats like videos, carousels, and stories capture attention and drive meaningful interactions.", "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?auto=format&fit=crop&w=800&q=80"),
            ("Lead Generation &amp; Sales", "Paid ads help you collect leads, drive website traffic, and improve conversions with measurable ROI.", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80"),
            ("Remarketing Opportunities", "Retarget people who already interacted with your brand — turning interest into action.", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"),
            ("Data &amp; Insights", "Every campaign delivers analytics — helping you refine strategies and create the <strong>best social media ad campaigns</strong>.", "https://images.unsplash.com/photo-1543286386-713bdd548da4?auto=format&fit=crop&w=800&q=80"),
        ],
        "best_campaigns": {
            "heading": "Best Social Media Ad Campaigns That <span class=\"green_text\">Deliver</span>",
            "body": "What sets our work apart is the way we combine creativity with analytics. We don't just run ads — we build campaigns that leave a lasting impression. Whether it's a video campaign designed to generate buzz or a retargeting strategy that brings back interested buyers, our focus is always on creating the <strong>best social media ad campaigns</strong> for long-term success.",
            "sub_heading": "Let's Build Your Next Campaign",
            "sub_body": "Ready to make your brand stand out with <strong>paid advertising social media</strong> strategies? Our team is here to help you design, launch, and scale campaigns that drive real impact. Connect with our <strong>paid social media agency</strong> today and take the first step toward growing your business with confidence.",
            "img": "https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=900&q=80",
            "side": "left",
        },
        "faqs": [
            ("What is paid advertising on social media?", "Paid advertising on social media involves running social ad campaigns on platforms like Facebook, Instagram, LinkedIn, and YouTube targeting specific audiences. Unlike organic posts, paid ads are targeted, measurable, and designed for faster results including leads, sales, or brand awareness."),
            ("Why should I choose a paid social media agency?", "Working with specialists ensures campaigns are backed by strategy, creative design, and continuous optimization. Rather than blind spending, experts help establish goals, identify target audiences, and run campaigns maximizing ROI."),
            ("How are paid social media campaigns different from organic posts?", "Organic posts develop long-term engagement but struggle with limited reach due to algorithms. Paid campaigns guarantee visibility by targeting users based on demographics, interests, and behaviors — delivering quicker, more scalable outcomes."),
            ("Which platforms are best for social media ad campaigns?", "Platform selection depends on goals and audience. Facebook and Instagram work best for broad consumer reach; LinkedIn excels for B2B lead generation; YouTube video ads suit storytelling and brand visibility. Strong strategy often combines multiple platforms."),
            ("How much should I budget for social media campaigns?", "Budgets vary by industry, goals, and competition. Some start at ₹20,000 monthly; others scale into larger amounts. The key is focusing on ROI — well-structured campaigns often generate returns exceeding spend."),
            ("How do you measure the success of social media ad campaigns?", "Key metrics tracked include impressions, clicks, conversions, cost per lead (CPL), and return on ad spend (ROAS). Detailed reporting shows exactly how campaigns perform and where improvements can occur."),
            ("What makes DigiVeritaz different from other agencies?", "Our focus is on creating campaigns blending creativity with performance. From video-led ads to retargeting funnels, innovation combines with data-driven insights — ensuring brands receive results, not vanity metrics."),
        ],
        "cta": ("Ready to grow your <span>brand?</span>", "Book your free consultation today and let's design campaigns that deliver measurable impact."),
    },
    "pay-per-click.html": {
        "title": "PPC Agency in India | Google Ads Management &amp; PPC Campaign Optimization | DigiVeritaz",
        "desc": "Pay-Per-Click advertising that turns clicks into customers. End-to-end Google Ads management, Shopping, Display &amp; Video campaigns with full-funnel tracking, CRO and ROI-focused optimization.",
        "h1": "Pay-Per-Click (PPC) <span class=\"green_text\">Advertising</span>",
        "crumb": "Home / Services / Pay Per Click",
        "kicker": "Drive Instant Visibility and Conversions with PPC",
        "intro": "When you want fast, measurable results, there is nothing quite like Pay-Per-Click. At DigiVeritaz, we turn clicks into customers — not just traffic. Whether you're a small startup or an established business, our <strong>PPC campaign management</strong> services ensure that every rupee you spend delivers value by targeting ready-to-buy audiences and optimising for maximum ROI.",
        # Why PPC Is Essential — split panel with bullets + CTA, image on right
        "highlights": [
            {
                "heading": "Why PPC Advertising Is <span class=\"green_text\">Essential For Your Business?</span>",
                "intro": "PPC gives your business the speed, precision and accountability that organic channels can't deliver. Five reasons it belongs in every growth plan:",
                "bullets": [
                    ("Immediate Presence", "Appear at the top of search engine results the moment you launch a campaign."),
                    ("Controlled Budgeting", "Only pay when users click (or convert), ensuring efficient spend."),
                    ("Highly Targeted", "Reach people by location, device, keyword and behaviour — no more shooting in the dark."),
                    ("Measurable Results", "Track everything — from clicks and impressions to CPA and ROAS."),
                    ("Flexibility &amp; Testability", "Test ad copies, landing pages, bid strategies and creatives — then scale what works."),
                ],
                "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
                "side": "right",
                "cta_text": "Launch Your Brand With Us",
            },
        ],
        # Our PPC Services — 6 sub-service cards (merged tracking into optimization)
        "sub_services": [
            ("strategy", "Strategy &amp; Planning", "Keyword research, competitor audits, target audience profiling and defining conversion paths for every campaign."),
            ("ppc", "Campaign Setup", "Setting up Google Ads, Display Network, Shopping Ads and Video Ads — structured by theme, ad group and keyword match types."),
            ("brand", "Creative Development", "Ad copywriting, designing banners &amp; display creatives, video script + assets, and rigorous A/B testing."),
            ("growth", "Landing Page &amp; Conversion Optimization", "Ensuring landing pages are relevant, fast, mobile-friendly and persuasive; optimising forms and CTAs for conversion."),
            ("perf", "Bid Management &amp; Budget Allocation", "Smart bidding strategies (manual, automated, ROAS-based) — adjusting bids by device, time and geography."),
            ("data", "Ongoing Optimisation &amp; Reporting", "Refining negatives, rotating creatives, testing extensions, and transparent dashboards for KPIs like CPC, CPA and ROAS."),
        ],
        # Why Choose DigiVeritaz — split panel with bullets + CTA, image on left
        "highlight": {
            "heading": "Why Choose DigiVeritaz As Your <span class=\"green_text\">PPC Partner?</span>",
            "intro": "We combine Mumbai roots with global PPC playbooks — backed by certified experts and a framework built around continuous optimisation:",
            "bullets": [
                ("Google Ads Agency In Mumbai, India-Wide Reach", "We understand local, national and international markets — combining global best practices with local insight."),
                ("Certified Google Ads Experts", "Certified Google Ads experts, seasoned PPC specialists and consultants who live &amp; breathe paid search."),
                ("Proven Track Record", "Improving Quality Score, lowering CPC, boosting CTR and increasing conversion rates — monitor daily, refine weekly, scale monthly."),
                ("Hands-On Google Ads Consultant", "Advising on budget, strategy and growth — responsive and accessible whenever you need us."),
                ("Transparent Reporting", "No hidden fees. You know where every rupee goes and what it delivers."),
            ],
            "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80",
            "side": "left",
            "cta_text": "Launch Your Brand With Us",
        },
        # Process — 8 steps
        "process": [
            ("Discovery &amp; Audit", "We begin by understanding your business, goals, cash flow, competition and existing digital footprint — auditing current PPC campaigns, website and conversion paths."),
            ("Keyword &amp; Market Research", "Using tools and human insight, we find profitable, relevant keywords (including long-tail) — understanding search trends, volume, region and seasonality."),
            ("Strategy &amp; Campaign Architecture", "Define the structure: campaigns per objective (brand awareness, sales, lead gen), ad groups per theme, match-types and targeting."),
            ("Ad Copy, Creative &amp; Extensions", "Craft compelling ad copy aligned with user intent. Use ad extensions (sitelinks, callouts, calls) and design display/video creatives."),
            ("Tracking &amp; Infrastructure Setup", "Proper conversion tracking (form fills, calls, purchases), GA4, tagging, audience lists and remarketing setup."),
            ("Launch &amp; Monitor", "Launch with initial bids and budgets. Monitor impressions, clicks, spend and early conversions — adjust for budget pacing."),
            ("Optimisation &amp; Scaling", "Refine negative keywords, pause under-performers, test copy/creative, adjust bids by time/device/geo, and scale up where ROI is positive."),
            ("Reporting &amp; Insights", "Regular reports showing spend, CPC, CPA, conversion rate, ROAS with insights and recommendations — dashboards for full transparency."),
        ],
        # Types of Ads &amp; Platforms — 6 cards
        "platforms_intro": "Our expertise spans every major ad format and placement — matching the right channel to your objective.",
        "platforms": [
            ("search", "Search Ads", "Google Search &amp; Bing — reach users actively searching for your product or service."),
            ("display", "Display Ads", "Visual banners across Google Display Network and partner websites — ideal for awareness &amp; remarketing."),
            ("shopping", "Shopping Ads", "For e-commerce — show product image, title and price directly in search engine results."),
            ("yt", "Video Ads", "YouTube and video placements to tell brand stories or product demos at scale."),
            ("remarket", "Remarketing &amp; Retargeting", "Re-engage users who visited but didn't convert — the highest-ROI segment on any account."),
            ("app", "App Install Ads", "If you have an app, we run campaigns to acquire users cost-effectively across Google and YouTube."),
        ],
        "platforms_outro": "No matter the ad format, every campaign is tuned for your business objective — not vanity metrics.",
        # How We Ensure ROI
        "simple_benefits": {
            "heading": "How We Ensure <span class=\"green_text\">ROI &amp; Continual Growth</span>",
            "items": [
                "<strong>Quality Score Improvements</strong> — better QS means lower CPC and better ad rank.",
                "<strong>Ad Relevance &amp; UX</strong> — copy-to-landing-page alignment, fast pages and mobile optimisation.",
                "<strong>Smart Bidding</strong> — Google's machine learning (target CPA, ROAS) applied where the data supports it.",
                "<strong>Budget Efficiency</strong> — shift spend from low-ROI to high-performing campaigns; cut waste via negative keywords.",
                "<strong>Creative Refresh</strong> — new visuals and copy to combat ad fatigue.",
                "<strong>Trend &amp; Seasonal Adjustments</strong> — sale seasons, festivals and market shifts factored in.",
            ],
        },
        "faqs": [
            ("What is PPC campaign management, and why do I need it?", "PPC campaign management is the end-to-end process of planning, launching, monitoring, optimizing and scaling paid campaigns (Google Ads, Bing, Display/Video). Without expert management, ad spend gets wasted on irrelevant clicks, poor creatives or wrong targeting. We structure campaigns for efficient performance, track metrics and adjust strategies to ensure real business results."),
            ("How soon will I see results from a PPC campaign?", "You'll see initial results (impressions, clicks) almost immediately after launch. However, meaningful outcomes like stable conversions, lower CPA and good ROAS usually take 2–4 weeks of data gathering and optimization. Some verticals may need longer to test creatives and keywords."),
            ("What makes a good Google Ads agency?", "Look for Google certifications/partner status, case studies relevant to your industry and location, transparent reporting with clear metrics (CPC, CPA, ROAS), experience in PPC campaign optimization, and strong communication with ability to adjust quickly."),
            ("How do you determine budget and bidding strategy?", "We assess your business goals (leads, sales, brand awareness), industry competition, keyword costs, expected conversion rates and profit margins. From there we recommend a realistic monthly budget. For bidding, depending on data and campaign maturity, we use manual, enhanced CPC, target CPA or target ROAS bidding."),
            ("Which keywords should I pay for, and which ones should I avoid?", "Pay for keywords aligned with intent (e.g. 'buy shoes online', 'best accounting software'), long-tail keywords, local keywords where relevant, and branded terms. Avoid generic queries with low conversion intent ('download free', 'info about'), irrelevant match types, and competitor brand names when not beneficial."),
            ("Are there common PPC mistakes to watch out for?", "Not using negative keywords, allowing ad fatigue (same ads too long), poor landing page experience, mismatched ad copy and landing page messaging, overbidding without monitoring return, and failing to track conversions properly."),
            ("How do you measure success of a PPC campaign?", "Key metrics include Cost Per Click (CPC), Click-Through Rate (CTR), Cost Per Acquisition (CPA), Conversion Rate, Return On Ad Spend (ROAS), Quality Score and Impression Share — all reported via dashboards so you understand what's working and what's not."),
            ("Is PPC expensive? How much should I expect to invest?", "PPC isn't cheap but when done right it pays off. Costs vary by industry, keyword competitiveness and geography. Small businesses often start at ₹30,000–₹60,000/month; larger brands investing across multiple channels spend significantly more. What matters is ROI — a well-managed campaign typically pays for itself many times over."),
            ("Can small or local businesses benefit from PPC?", "Absolutely. Local businesses see excellent results targeting 'near me' keywords, geo-targeted ads and mobile audiences. As a Google Ads agency in Mumbai, we understand those local levers deeply."),
            ("Do you offer ongoing optimization or just initial setup?", "Continuous improvement is built into every engagement — analysing performance, refining based on data, scaling what works and cutting what doesn't. Setup is the starting line, not the finish."),
        ],
        "cta": ("Ready to stop leaving clicks <span>on the table?</span>", "Get a free PPC audit — we'll benchmark your current campaigns, identify what's working and what's not, and give you actionable recommendations with budget estimates."),
    },
    "performance-marketing-agency.html": {
        "title": "Performance Marketing Agency in India &amp; Mumbai | DigiVeritaz",
        "desc": "Performance marketing agency in Mumbai &amp; India delivering measurable growth — CRO, lead generation, paid media, app installs and revenue-driven campaigns tied to CPL, CPA and ROAS.",
        "h1": "Performance Marketing <span class=\"green_text\">Agency</span>",
        "crumb": "Home / Services / Performance Marketing",
        "kicker": "Driving Measurable Growth With Performance Marketing",
        "intro": "In a crowded digital marketplace, you need more than visibility — you need performance. Our <strong>performance marketing agency in India</strong>, specifically in Mumbai, delivers results that matter. We don't chase impressions or likes — we focus on conversion, retention and revenue. If you're looking for a <strong>lead generation specialist</strong>, an agency that nails <strong>conversion rate optimization</strong>, or someone to meaningfully boost your social media reach, you've come to the right place.",
        # What Is Performance Marketing — split panel with body + bullets
        "highlights": [
            {
                "heading": "What Is <span class=\"green_text\">Performance Marketing?</span>",
                "body1": "Performance marketing refers to digital marketing strategies and campaigns driven by results — typically measurable actions like leads, sales and app installs. <strong>Every rupee spent is tied to a KPI.</strong>",
                "body2": "If we don't deliver results, you don't pay (or you don't invest much beyond guaranteed minimums). Core pillars:",
                "bullets": [
                    ("Tracking &amp; Analytics", "Every campaign instrumented before launch."),
                    ("Optimisation", "Landing pages, funnels and UX continuously refined."),
                    ("Precise Audience Targeting", "Reach only the people who can convert."),
                    ("A/B Testing &amp; Experimentation", "Data-led decisions, not opinions."),
                    ("ROI-Focused Budget Allocation", "Every rupee chases a measurable outcome."),
                ],
                "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
                "side": "right",
            },
        ],
        # Our Services — 6 cards
        "sub_services": [
            ("growth", "Conversion Rate Optimization (CRO)", "Improve your website and landing pages to get more of your existing traffic to take desired actions — form fills, purchases, sign-ups and beyond."),
            ("lead", "Lead Generation Agency Support", "We act as your <strong>lead generation specialist</strong> — doing everything from audience research to campaigns that produce high-quality leads, not just traffic."),
            ("ppc", "Paid Media (Search / Social / Display)", "Targeted ads on Google, Facebook, Instagram, LinkedIn — budget management, creative testing and bid optimisation baked in."),
            ("app", "App Installs &amp; Mobile Marketing", "Drive new users to your mobile app with performance-driven campaigns tuned for install cost and Day-7 retention."),
            ("social", "Social Media Boost", "Not just engagement — we boost reach, conversions and audience growth through organic + paid strategies aligned with your funnel."),
            ("revenue", "Revenue-Driven Campaigns", "Campaigns engineered for real business growth — more transactions, higher order value and repeat purchases."),
        ],
        # Why Choose Us — split panel with bullets + CTA, image on left
        "highlight": {
            "heading": "Why Choose Us As Your <span class=\"green_text\">Performance Marketing Agency</span>",
            "intro": "We combine local Mumbai roots with global performance frameworks — and a commitment to full-funnel thinking, not last-click worship:",
            "bullets": [
                ("Data-First Approach", "Every campaign begins with research, analytics and KPI setup — we measure what matters, not vanity metrics."),
                ("Local Expertise, Global Standards", "As a performance marketing agency in Mumbai, we understand local audiences and culture while applying world-class frameworks."),
                ("Full-Funnel Optimisation", "We don't stop at clicks — we see the full journey from awareness → consideration → conversion → retention."),
                ("Agile &amp; Transparent Execution", "Frequent reporting, testing and iteration. You always know what's working, what isn't, and where your budget is going."),
                ("Cross-Channel Synergy", "Search, social, native, display and app — all working together for compound impact, not siloed outcomes."),
            ],
            "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80",
            "side": "left",
            "cta_text": "Launch Your Brand With Us",
        },
        # Our Process — 7 steps
        "process": [
            ("Discovery &amp; Audit", "Understanding your business, target audience, competitors — plus an audit of your current digital footprint, landing pages, ads and analytics."),
            ("Strategy Planning", "Define KPIs (leads, conversion rate, CPL, CPA). Build channel strategy (search, social, display, remarketing) with budget and media plan."),
            ("Creative &amp; Copy Development", "Engaging creatives and messaging designed to convert — not just catch the eye. Includes landing page design and optimisation."),
            ("Execution &amp; Media Buying", "Launch campaigns, monitor performance, apply bid strategies, audience targeting and retargeting funnels from day one."),
            ("Conversion Rate Optimisation Service", "A/B test landing pages and ad copy. UX/UI improvements. Funnel drop-off analysis until the numbers move."),
            ("Tracking, Analytics &amp; Reporting", "Full-funnel tracking (first click, last click, assisted conversions). Regular dashboards with insights on what to scale and what to cut."),
            ("Iterative Optimization", "Based on data, refine audiences, creative and channels. Reallocate budget to best performers. Continuous improvement every sprint."),
        ],
        # Case Use-Scenarios
        "simple_benefits": {
            "heading": "Who <span class=\"green_text\">We Help</span>",
            "items": [
                "<strong>E-Commerce brands</strong> wanting to reduce cart abandonment and scale sale events.",
                "<strong>SaaS / B2B companies</strong> needing high-quality leads through search, LinkedIn and content-driven tactics.",
                "<strong>Apps &amp; Startups</strong> aiming for installs, activation and Day-7 engagement.",
                "<strong>Local businesses</strong> in Mumbai / India wanting footfall, calls or service bookings.",
                "<strong>Growth-stage teams</strong> looking for transparent pricing and ROI forecasts.",
                "<strong>In-house marketing teams</strong> that need a performance pod filling creative, media or analytics gaps.",
            ],
        },
        "faqs": [
            ("What is the difference between a performance marketing agency and a traditional digital marketing agency?", "Traditional digital marketing often focuses on brand awareness, impressions, traffic and social following. Performance marketing specifically ties spend to measurable outcomes — leads, purchases and conversions. You pay for results, or optimise toward them."),
            ("How long before I'll see ROI?", "It depends on your industry, competition, product price point, budget and the strength of your current funnel, website and creatives. Initial testing and learning typically takes 2–4 weeks. Significant ROI is usually seen in 8–12 weeks once optimisation cycles are running."),
            ("How much budget is needed to start?", "Minimum budgets depend on channel and competition. Local Mumbai campaigns may need less; national/international scale or high-CPC verticals (finance, education) need more. We work closely with you to map expected outcomes vs. budget."),
            ("Will you manage everything — creative, ad spend, optimisation, tracking?", "Yes. We typically offer end-to-end performance marketing services: creative and copy, landing pages, audience targeting, media buying, optimisation, analytics and reporting. If you have in-house resources, we collaborate or fill gaps."),
            ("What types of businesses do you serve?", "We've worked with e-commerce, local service, SaaS, startups, apps, retail, education and hospitality clients. If your business needs a lead generation agency, social media boost, or CRO service — we have packages tailored for you."),
            ("Why choose a performance marketing agency in Mumbai / India over overseas or doing it in-house?", "Local presence means better cultural relevance, language nuance, faster communication and a stronger read on consumer behaviour. There's also a cost advantage — combined with global best practices, data-driven tools and cross-border learnings."),
            ("How is performance tracked and reported?", "We set up dashboards (Google Analytics, Tag Manager, ad-platform dashboards) and define KPIs in advance. Reports are weekly or bi-weekly — you'll always know your cost per lead, cost per acquisition and return on ad spend."),
        ],
        "cta": ("Ready to turn spend into <span>measurable growth?</span>", "Book a free consultation and PPC audit — we'll benchmark your current campaigns and return a growth plan within 48 hours."),
    },
    "ecommerce-marketing.html": {
        "title": "E-Commerce Managed Services | Amazon, Flipkart, Shopify | DigiVeritaz",
        "desc": "E-commerce platforms managed services that scale your online business across Amazon, Flipkart, Shopify and D2C — white-label operations, performance marketing, analytics dashboards and end-to-end growth.",
        "h1": "E-Commerce <span class=\"green_text\">Platforms</span>",
        "crumb": "Home / Services / E-Commerce",
        "kicker": "Managed Services That Scale Your Online Business",
        "intro": "We don't just help you go live online — we partner with you to thrive. Our <strong>e-commerce management services</strong> are designed to help brands compete, convert and scale across marketplaces and independent webstores. Whether you're an established retailer or an emerging D2C brand, we bring performance marketing, analytics, customer experience and platform operations under one roof — and deliver as a white-label service so your brand always stays front and centre.",
        "highlights": [
            {
                "heading": "Why <span class=\"green_text\">E-Commerce Managed Services</span> Matter Now",
                "body1": "Consumer expectations keep rising — faster shipping, richer product information, hassle-free returns, omnichannel trust. Marketplaces are getting more competitive, ad costs are climbing, and inventory-fulfilment inefficiencies silently eat into margin.",
                "body2": "By adopting a managed service model with a <strong>white-label e-commerce platform</strong> and strong <strong>ecommerce dashboard</strong> insights, you position your business to grow smart — not just bigger.",
                "bullets": [
                    ("Faster Shipping &amp; Better UX", "Meet rising customer expectations without internal overhead."),
                    ("Marketplace Competitiveness", "Win visibility and stay compliant across Amazon, Flipkart, Myntra."),
                    ("Smarter Ad Spend", "Optimise across channels as paid complexity grows."),
                    ("Inventory &amp; Margin Control", "Fix the silent profit killers — forecasting, 3PL, returns."),
                ],
                "img": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=900&q=80",
                "side": "right",
            },
        ],
        # What We Offer — 6 core service pillars
        "sub_services": [
            ("strategy", "Platform &amp; Marketplace Setup", "Onboarding to marketplaces and webstore platforms. <strong>White-label e-commerce platform</strong> deployment with custom storefront, branding, UI/UX, product catalogs, attribute taxonomies and category structures."),
            ("content", "Product &amp; Catalog Management", "Product data, variations, description writing and imagery QC. Price management, discounting, promotions and bundling — with SEO for product pages and keyword-optimised titles."),
            ("data", "Order, Inventory &amp; Fulfillment", "Order processing, stock monitoring and forecast planning. Returns and exchange management plus integration with warehousing, 3PL and logistics partners."),
            ("ppc", "E-Commerce Advertising", "Sponsored listings on Amazon, Flipkart and more. Display, Social and Google Shopping for your webstore — with A/B testing, bid optimisation and seasonality-aware planning."),
            ("perf", "Analytics, Dashboards &amp; Reporting", "Ecommerce dashboard covering sales, traffic, conversion, ACOS/ROAS, lifetime value and churn. Regular insights, strategy sessions and competitor benchmarking."),
            ("chat", "Ongoing Account Management", "Dedicated account managers, inventory alerts, compliance management, seasonal refreshes and reviews/ratings moderation."),
        ],
        # Why Choose DigiVeritaz — split panel with bullets + CTA
        "highlight": {
            "heading": "Why Choose <span class=\"green_text\">DigiVeritaz</span>",
            "intro": "Five differentiators that turn a managed service from a cost line into a growth engine:",
            "bullets": [
                ("White-Label Approach", "We build your store or marketplace presence under <strong>your brand</strong>. We don't rebrand ourselves — it's your e-commerce platform, powered by us."),
                ("End-to-End Capability", "Strategy, platform selection, analytics and customer care — a full-stack service where every piece feeds into the next."),
                ("Data-First, Performance-Driven", "Every decision grounded in data. Your dashboard shows which products drive profit, which campaigns work and what levers to pull."),
                ("Scalability &amp; Flexibility", "From 10 SKUs to thousands, one marketplace to many, seasonal bursts to year-round growth — we scale with you."),
                ("Compliance &amp; Risk Mitigation", "Marketplace rules, tax regimes, shipping policies and returns — handled, so you avoid penalties, takedowns and trust issues."),
            ],
            "img": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80",
            "side": "left",
            "cta_text": "Launch Your Brand With Us",
        },
        # Process — 5 stages
        "process": [
            ("Discovery &amp; Audit", "We audit your existing presence — webstore, marketplace accounts, ad spend, inventory and operational gaps — then map them to business goals around growth, margin and reach."),
            ("Strategic Roadmap &amp; Platform Blueprint", "Based on the audit, we propose platforms to use, product lines to prioritise, a promotional calendar, the tech stack and staffing or partner needs."),
            ("Implementation &amp; Setup", "Deploy chosen platforms, configure dashboards, set up ad accounts, integrate logistics partners, list your products and onboard your staff."),
            ("Launch &amp; Go-Live Support", "When you're ready to sell, we make sure the store is optimised, promotions are live and the customer experience is smooth — with real-time monitoring to fix issues fast."),
            ("Ongoing Management &amp; Growth", "The long game — account management, ads &amp; campaigns, regular performance reviews, continuous optimisation and expansion to new channels."),
        ],
        # Dashboard deliverables (What You'll Get)
        "simple_benefits": {
            "heading": "Your <span class=\"green_text\">Ecommerce Dashboard</span> — A Single Control Centre",
            "items": [
                "<strong>Sales</strong> by product, category &amp; channel (marketplace vs. webstore).",
                "<strong>Conversion metrics</strong> — product page CVR, cart abandonment and checkout drop-off.",
                "<strong>Ad performance</strong> — spend, impressions, clicks, ROAS and ACOS.",
                "<strong>Inventory health</strong> — status, forecast and turnover rates.",
                "<strong>Fulfilment metrics</strong> — shipping time, return rate and customer complaints.",
                "<strong>Customer metrics</strong> — repeat purchase rate, AOV and lifetime value.",
            ],
        },
        # Typical Engagements & Packages (3 tiers)
        "packages": {
            "heading": "Typical Engagements &amp; <span class=\"green_text\">Packages</span>",
            "intro": "Though each business is unique, here are sample models / tiers to give you an idea:",
            "tiers": [
                ("Starter", "Smaller D2C brands, 1 platform, limited SKUs", "3–6 Months", "Platform setup, basic product &amp; catalog management, light advertising, standard dashboard reports."),
                ("Growth", "Brands scaling SKUs, multiple platforms / marketplaces", "6–12 Months", "Full product &amp; inventory integration, mid-level performance marketing, advanced dashboards, account manager, compliance management."),
                ("Enterprise", "Big brands, multiple regions, aggressive targets", "1 Year Plus + Continuous Support", "White-label platform customisations, high-spend ad campaigns, localisation, international marketplaces, custom reporting, integrations (ERP, logistics)."),
            ],
        },
        "faqs": [
            ("What is included under an 'ecommerce managed service'?", "End-to-end support: platform setup, product &amp; inventory management, order fulfilment, returns/logistics coordination, ad campaign management, analytics &amp; reporting, compliance and ongoing optimization — all under one engagement."),
            ("What does 'white label e-commerce platform' mean?", "A platform or storefront branded as <em>your</em> store — your logo, design, UI/UX, domain — while the backend operations, tech and maintenance are handled by us. The customer-facing interface is yours; the infrastructure and operations are ours."),
            ("How do you measure success? Which KPIs do you track?", "Key metrics: conversion rate, average order value, repeat purchase rate, return rate, ROAS/ACOS, inventory turnover, gross margin and customer lifetime value. Your ecommerce dashboard gives real-time visibility on all of these."),
            ("Can you manage both marketplaces and standalone webstores?", "Absolutely. We manage Amazon, Flipkart, Myntra and your own Shopify / WooCommerce / Magento store. Coordinating across channels is critical to avoid stock issues, mismatched branding or conflicting promotions."),
            ("How quickly can you get started, and when will I see results?", "We begin within 1–2 weeks of agreement. Platform and catalog setup takes a few weeks; early returns (traffic, small sales) can appear quickly with ads; sustainable performance — repeat customers, healthy margins — typically shows in 3–6 months."),
            ("What do you deliver vs. what I deliver?", "We provide the full backend service. Your team typically contributes decisions on assortment, branding guidelines, pricing and promo approvals. You may also provide product content and photography — or we can source them for you."),
            ("How do you handle compliance, returns and marketplace policy?", "We monitor marketplace rules closely — listings, content claims, policies. Returns, exchanges and refunds are handled via platform or your logistics partners. We also manage dispute resolution, negative-review moderation and product compliance certifications where required."),
            ("Is the ecommerce dashboard an extra charge?", "It's included in most plans. Customised dashboards or real-time integrations with external systems (ERP, warehouse) may have additional fees — these are always included transparently in the quote up front."),
        ],
        "cta": ("Ready to scale your <span>online business?</span>", "Book your free consultation today — we'll audit your current presence and return a custom growth plan within 48 hours."),
    },
    "data-strategy-consulting-services.html": {
        "title": "Data Strategy &amp; Consulting Services | Analytics, GA4, Dashboards | DigiVeritaz",
        "desc": "Data strategy and consulting services for growth-stage brands — GA4 setup, dashboards (Looker Studio, Power BI, Tableau), attribution, governance and measurement frameworks that drive real decisions.",
        "h1": "Data Strategy &amp; <span class=\"green_text\">Consulting Services</span>",
        "crumb": "Home / Services / Data Strategy",
        "kicker": "Extract Real Insight — Don't Just Amass Numbers",
        "intro": "In an environment overflowing with data, what truly matters is <strong>extracting real insight</strong> and using it to fuel growth — not just amassing numbers. At DigiVeritaz, our Data Strategy &amp; Consulting service partners with businesses to build strong data foundations, make sense of complex information, and transform insights into action.",
        "highlights": [
            {
                "heading": "Why Data Strategy <span class=\"green_text\">Matters</span>",
                "intro": "Without a solid data strategy, metrics disconnect from business goals, insights get lost in silos and decisions default to gut feel. A good strategy fixes all four:",
                "bullets": [
                    ("Aligning Purpose With Measurement", "Every KPI traces back to a larger objective — growth, efficiency, satisfaction or retention."),
                    ("Consistency, Accuracy &amp; Trust", "Unified definitions and clean data hygiene across web analytics, CRM, social and internal logs."),
                    ("Scalability &amp; Flexibility", "Strategies that accommodate new pipelines and evolve with market shifts without collapsing under complexity."),
                    ("Competitive Advantage", "Faster insights, trend prediction, optimised operations and more tailored customer responses."),
                ],
                "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80",
                "side": "right",
                "cta_text": "Launch Your Brand With Us",
            },
        ],
        "sub_services": [
            ("strategy", "Discovery &amp; Audit", "A deep dive into your current systems, data pipelines and reporting methods — uncovering gaps, redundancies and quick wins with a clear picture of what's working and what needs attention."),
            ("data", "Strategy &amp; Planning", "We craft a data strategy aligned with your business objectives — defining KPIs, recommending tools, setting governance policies and mapping a phased roadmap for success."),
            ("perf", "Implementation &amp; Systems", "Reliable data pipelines, platform integrations (CRM, analytics) and dashboards that visualise metrics that matter — with tracking, validation and quality checks baked in."),
            ("growth", "Analytics &amp; Insights", "Beyond setup — advanced statistical methods, segmentation and predictive models that reveal customer behaviour, trends and growth opportunities."),
            ("revenue", "Optimization &amp; Ongoing Support", "Data isn't a one-time project. Business analytics consulting on retainer — fine-tuning dashboards, testing campaigns and adjusting strategy as you evolve."),
            ("content", "Data-Driven Content Support", "Data shows what's happening — words move people. We layer copywriting and content production on top of insights so every asset is shaped by performance data."),
        ],
        "highlight": {
            "heading": "Why Choose <span class=\"green_text\">DigiVeritaz</span>",
            "intro": "You're not just getting generic dashboards — you're getting partners who blend domain, technical and communication expertise:",
            "bullets": [
                ("Integrated Expertise", "Data consulting, content and analytics aren't silos — we weave them together for compounding impact."),
                ("Accountability &amp; Transparency", "Everything is measurable. KPIs, progress tracking and regular reports — adjusted until outcomes move."),
                ("Proven Method", "A structured, tested process refined with many clients — we know what works, what stalls and what needs special attention."),
                ("Clear Communication", "Complex insights are useless if stakeholders don't understand them. We simplify analytics so technical and non-technical teams both get it."),
                ("Commitment To Your Growth", "You succeed when strategies deliver real business value — higher conversions, lower costs, better engagement."),
            ],
            "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
            "side": "left",
            "cta_text": "Launch Your Brand With Us",
        },
        "process": [
            ("Discovery Call", "Get to know your business, challenges, data sources, decision processes, who uses data and what pain points exist today."),
            ("Audit Of Current State", "Review your existing tools, dashboards, tracking setup, reports, data sources and content performance for a baseline."),
            ("Strategy Workshop", "Define goals, metrics, roadmap, responsibilities, pipelines and any new tools required — all aligned to business outcomes."),
            ("Implementation Phase", "Set up tracking, dashboards and data flows. Integrate platforms. Kick off content based on early insights."),
            ("Insight &amp; Analytics Phase", "Regular reporting, trend analysis, content performance reviews and meetings to interpret data and propose next actions."),
            ("Optimization &amp; Scaling", "As results come in, iterate. Introduce predictive models. Scale content and campaigns that perform best."),
            ("Training &amp; Transition", "We train internal stakeholders so analysis, content and strategy continue confidently even after our engagement ends."),
        ],
        "simple_benefits": {
            "heading": "Key Benefits Of Our <span class=\"green_text\">Data Strategy &amp; Consulting</span>",
            "items": [
                "<strong>Clearer visibility</strong> into what's working — and what's not — for faster course corrections.",
                "<strong>Higher ROI from marketing spend</strong>, because we stop guessing and start measuring.",
                "<strong>Better alignment across teams</strong> — everyone works off the same data and definitions.",
                "<strong>More engaging content</strong>, because messaging comes from real consumer insights.",
                "<strong>Reduced risk</strong> — decisions based on data, not gut feelings.",
                "<strong>Future-ready measurement</strong> — server-side tracking and privacy-first data models.",
            ],
        },
        "industries": ["Digital Marketing-Heavy Brands", "Scaling SMEs", "Product Launches", "New Market Entry", "Content Publishers", "Enterprise Data Teams"],
        "faqs": [
            ("How long does a full strategy implementation take?", "For SMEs, a complete audit, roadmap and initial setup usually takes 6–10 weeks. For large enterprises with multiple departments and complex systems, it can extend to a few months."),
            ("What tools do you use?", "Google Analytics (GA4), Looker Studio, Power BI and Tableau for reporting and visualisation. CRM integrations (HubSpot, Salesforce, Zoho) and ad platforms for performance tracking. ETL and data-pipeline tools for automation and real-time updates."),
            ("Do you also provide content writing (blogs, landing pages, ads)?", "Yes — we integrate copywriting and content writing into our service. Content is shaped by data insights (topics, keywords, customer intent) to maximise ROI."),
            ("Is this just for big companies?", "No — our business analytics consulting is scalable. Startups and SMEs get lean, cost-effective frameworks. Enterprises benefit from advanced data governance, predictive modelling and scalable dashboards."),
            ("Can you train our internal teams?", "Yes — we provide workshops and hands-on training on data literacy, dashboard reading and content strategy. The goal is to make your team independent and confident with data."),
            ("What ROI can we expect?", "Stronger alignment of marketing spend with conversions, increased decision-making efficiency, and reduced wastage by cutting underperforming campaigns and doubling down on proven ones."),
            ("Do you handle server-side tracking and privacy compliance?", "Yes — server-side GA4, Conversion API for Meta/Google, consent-mode integrations and cookie-less tracking frameworks are all part of our modern measurement stack."),
        ],
        "cta": ("Ready to turn data into <span>decisions?</span>", "Book your free consultation — we'll audit your current measurement stack and return a strategy roadmap within two weeks."),
    },
    "native-advertising.html": {
        "title": "Native Advertising Services in India | DigiVeritaz",
        "desc": "Leading native advertising company in India combining platform expertise, creative finesse and programmatic optimization to deliver campaigns that move the needle.",
        "h1": "Native Advertising Services by <span class=\"green_text\">DigiVeritaz</span>",
        "crumb": "Home / Services / Native Advertising",
        "kicker": "Native Advertising",
        "intro": "As a leading native advertising company in India, we combine platform expertise, creative finesse and performance optimization to deliver native advertising services that move the needle — without feeling like ads.",
        "benefits": [
            ("Seamless Integration", "Ads blend with content, reducing interruption and boosting receptivity."),
            ("Higher Engagement &amp; CTR", "Outperform traditional display formats significantly."),
            ("Better Brand Perception", "Value-driven content builds trust, not ad fatigue."),
            ("Ad-Blocker Resilient", "Native formats bypass common blockers."),
            ("Programmatic Scalability", "Automated bidding and optimization at scale."),
            ("Strong ROI", "Lower CPC and higher engagement translate to better unit economics."),
        ],
        "deliverables": [
            "Native ad campaign planning &amp; execution",
            "Creative content production (articles, infographics, visual stories)",
            "Native display and in-feed ads",
            "Recommendation widget placements",
            "Sponsored content &amp; advertorials",
            "Programmatic native buying",
            "Platform partnerships &amp; publisher deals",
            "Multilingual &amp; regional campaigns",
        ],
        "process": [
            ("Research &amp; Platform Mapping", "Identify where native works for your audience and goals."),
            ("Creative &amp; Content Design", "Headlines and visuals that match each platform's aesthetic."),
            ("Campaign Setup &amp; Targeting", "Configure bidding, placements and audience segments."),
            ("Testing &amp; Optimization", "A/B test creatives and monitor engagement metrics."),
            ("Analytics &amp; Insights", "Conversion path analysis and performance dashboards."),
            ("Scaling &amp; Expansion", "Roll out winners across new publishers and regions."),
        ],
        "faqs": [
            ("How is native different from display advertising?", "Native ads blend into content environments visually and functionally — focused on integration and context. Display ads (banners, sidebars) feel overtly promotional."),
            ("Is native affordable for startups?", "Yes — with flexible budgets, strategic targeting, testing and gradual scaling, it works at many budget levels."),
            ("Timeline to results?", "Initial engagement metrics appear within days; meaningful conversions typically require 2–4 weeks of optimization."),
            ("How is compliance handled?", "Disclosure labels ('Sponsored', 'Promoted') and adherence to platform policies maintain user trust and regulatory alignment."),
            ("Can attribution be tracked?", "Yes — via UTM parameters, pixel integrations and conversion modeling."),
        ],
    },
    "whatsapp-marketing-services.html": {
        "title": "WhatsApp Marketing Services in India | Bulk Messaging &amp; Automation | DigiVeritaz",
        "desc": "WhatsApp Marketing services that drive real conversations — bulk messaging, AI chatbots, CRM integration and official WhatsApp Business API automation.",
        "h1": "WhatsApp Marketing Services That Drive <span class=\"green_text\">Real Conversations</span>",
        "crumb": "Home / Services / WhatsApp Marketing",
        "kicker": "WhatsApp Marketing",
        "intro": "In today's fast-moving digital world, your customers don't want another email — they want real-time communication. Our WhatsApp Marketing services help your business connect instantly, build trust and boost engagement through the world's most popular messaging app.",
        "benefits": [
            ("Bulk Messaging at Scale", "Reach thousands of contacts safely via the official API."),
            ("1:1 Personalization", "Names, purchase details and segment-specific messaging."),
            ("Automation &amp; Scheduling", "Greeting, order confirmation and feedback flows on autopilot."),
            ("AI-Powered Chatbots", "Convert inquiries into sales through intelligent chat flows."),
            ("CRM &amp; Landing Page Integration", "Closed-loop data from ad click to conversion."),
            ("Real-Time Analytics", "Delivery rates, responses and conversions tracked live."),
        ],
        "deliverables": [
            "Official WhatsApp Business API setup",
            "Bulk messaging platform &amp; campaign manager",
            "Audience segmentation &amp; personalization",
            "Chatbot automation &amp; AI chat flows",
            "Catalogue &amp; commerce integration",
            "CRM integration &amp; dedicated support",
        ],
        "process": [
            ("Discovery &amp; Use-Case Mapping", "Identify high-impact conversational touchpoints in your funnel."),
            ("WhatsApp Business API Setup", "Verified business number, API provisioning and compliance."),
            ("Audience &amp; Template Strategy", "Segment lists and design approved message templates."),
            ("Automation &amp; Chatbot Build", "Flows for greetings, confirmations, support and sales."),
            ("Launch, Monitor &amp; Optimize", "Campaign dashboards with real-time iteration."),
        ],
        "faqs": [
            ("What is the WhatsApp Business API and do I need it?", "The official WhatsApp Business API is required for bulk messaging, verified green-tick business accounts, chatbot automation and CRM integrations. If you plan to send more than a few messages a day or automate conversations, yes — you need the API."),
            ("Is bulk messaging on WhatsApp allowed?", "Only via the official Business API with approved message templates. Sending bulk messages from a regular WhatsApp account violates their terms and leads to number bans. We set you up the right way — fully compliant with Meta's policies."),
            ("How much does WhatsApp Marketing cost?", "There are two cost components: our setup &amp; management fee, and Meta's per-conversation charges (roughly ₹0.35–₹0.90 per message depending on type &amp; country). We help you forecast costs accurately based on your expected volume."),
            ("Can WhatsApp actually drive sales — not just notifications?", "Yes. Broadcast offers, abandoned-cart reminders, catalogue commerce and conversational sales flows consistently outperform email. Open rates are 90%+ vs. 20% for email, and click-through is 3–5× higher."),
            ("How quickly can we go live?", "For most brands, 7–10 business days: Meta business verification, API provisioning, template approvals, chatbot build and first broadcast. Enterprises with more complex CRM integrations may take 2–4 weeks."),
            ("Can you integrate WhatsApp with our CRM or Shopify?", "Yes — we integrate with Shopify, WooCommerce, HubSpot, Salesforce, Zoho, Freshdesk and custom CRMs via Zapier or direct API. So conversations, orders and customer data stay in sync."),
        ],
    },
    "branding-and-design.html": {
        "title": "Branding &amp; Design Services That Build Timeless Brands | DigiVeritaz",
        "desc": "Branding and design services that build timeless brands — strategy, identity, logo, packaging and brand systems crafted by experienced design professionals in Mumbai.",
        "h1": "Branding and Design Services That Build <span class=\"green_text\">Timeless Brands</span>",
        "crumb": "Home / Services / Branding &amp; Design",
        "kicker": "Branding &amp; Design",
        "intro": "We create brands that stand out, connect emotionally and convert. Our branding and design services go beyond a logo — we build a complete brand identity system that defines who you are, what you stand for, and how your audience remembers you.",
        "benefits": [
            ("Full-Service Creative Agency", "Concept to launch — strategy, identity, collateral, digital."),
            ("Custom-Built Identity", "Original ideas, not templates or mood-board clichés."),
            ("Cross-Industry Expertise", "Experienced designers across D2C, B2B, F&amp;B, education and more."),
            ("Strategy Meets Creativity", "Research-led positioning paired with bold visual execution."),
            ("Local Presence, Global Standards", "Based in Mumbai, delivering work at international quality."),
            ("Scalable Brand Systems", "Guidelines and templates so teams can ship on-brand at speed."),
        ],
        "deliverables": [
            "Brand Strategy Development",
            "Logo Design &amp; Brand Identity",
            "Rebranding Services",
            "Visual &amp; Corporate Identity Design",
            "Packaging &amp; Marketing Collateral",
            "Brand Guidelines &amp; Templates",
        ],
        "process": [
            ("Brand Discovery", "Understanding goals, audience and competitive landscape."),
            ("Strategy &amp; Positioning", "Defining the foundation for visual identity."),
            ("Design Exploration", "Presenting multiple design directions and routes."),
            ("Refinement &amp; Finalization", "Perfecting the chosen direction with brand guidelines."),
            ("Implementation Support", "Rolling out the brand across digital and offline platforms."),
        ],
        "faqs": [
            ("What's the difference between a logo and a brand identity?", "A logo is a single mark. A brand identity is the entire visual system — logo, colours, typography, imagery style, tone of voice, and the guidelines that keep everything consistent as your team scales."),
            ("How long does a branding project take?", "Rebrands typically take 6–10 weeks: 1–2 weeks discovery, 2–3 weeks strategy &amp; concepts, 2–3 weeks refinement, 1–2 weeks guidelines &amp; rollout. New brands from scratch are similar; full identity systems with packaging can run 10–14 weeks."),
            ("Will I get editable files and brand guidelines?", "Yes — you receive full editable source files (Illustrator, Figma), exported formats (SVG, PNG, PDF), and a brand guidelines document covering usage, do's and don'ts, typography, colour palettes and application examples."),
            ("Do you handle packaging, print collateral and merchandise design?", "Yes — packaging, stationery, marketing collateral, trade-show assets, merchandise and social media templates are all part of our branding offering. We think in systems, not one-offs."),
            ("Can you rebrand without losing existing equity?", "Absolutely. We run a brand audit first to identify what's worth carrying forward — recognisable marks, colour associations, taglines — and evolve the identity rather than reinventing from zero."),
        ],
    },
    "generative-search-optimisation.html": {
        "title": "Generative Search Optimisation (GEO) | Rank in AI Search | DigiVeritaz",
        "desc": "Generative Search Optimisation (GEO) services to rank your brand in ChatGPT, Google SGE, Perplexity, Bing Copilot and AI Overviews. Future-proof your organic visibility.",
        "h1": "Generative Search Optimisation <span class=\"green_text\">(GEO)</span>",
        "crumb": "Home / Services / GEO",
        "kicker": "Generative Search Optimisation",
        "intro": "The search landscape is changing fast. Traditional SEO was built around ranking for keywords — but today, users get their answers from AI-powered platforms like Google SGE, ChatGPT, Perplexity and Bing Copilot. We help your brand get cited in those answers.",
        "benefits": [
            ("Appear in AI Answers", "Citations in ChatGPT, Bing Copilot and Google SGE responses."),
            ("Enhanced Brand Authority", "Credible citations build generative trust signals."),
            ("Future-Proof SEO", "Stay visible as AI-driven search reshapes discovery."),
            ("Qualified Organic Conversions", "AI-referred users arrive with high intent."),
            ("Knowledge Graph Presence", "Strong entity signals that AIs can understand and cite."),
        ],
        "deliverables": [
            "Generative Visibility Audit",
            "Semantic content optimization",
            "Schema markup &amp; entity linking",
            "Generative Traffic Dashboard",
            "Continuous AI-model monitoring &amp; adaptation",
        ],
        "process": [
            ("Research &amp; Audit", "Identify AI visibility gaps and map competitor citations."),
            ("AI-Ready Content Structuring", "Semantic hierarchy and citation-friendly answers."),
            ("Technical GEO Implementation", "Schema markup and knowledge graph linking."),
            ("Generative Content Strategy", "Content engineered for AI summaries and chatbots."),
            ("Monitor, Analyze &amp; Adapt", "Track citations and adjust as AI models evolve."),
        ],
        "faqs": [
            ("What is Generative Search Optimisation (GEO)?", "GEO is the practice of optimising your brand, content and technical footprint so AI-powered answer engines — ChatGPT, Google SGE, Perplexity, Bing Copilot — cite you when users ask relevant questions. It's the evolution of SEO for the AI-search era."),
            ("Is GEO replacing SEO?", "No — it extends SEO. Traditional rankings still drive traffic; GEO adds visibility in AI answers where users increasingly spend research time. The tactics overlap (authority, schema, structured content) but add semantic structuring and citation-friendly formats on top."),
            ("How do you measure GEO success?", "Citation frequency across ChatGPT, Perplexity and Google SGE, share-of-voice for target entities, referral traffic from AI platforms, and brand-mention sentiment in AI responses. We report all of this in a Generative Traffic Dashboard."),
            ("How long does GEO take to show results?", "Faster than traditional SEO in some ways — AI models re-index content frequently. Initial citation pickups can happen in 4–6 weeks; stable presence in the top answers typically takes 3–4 months of consistent content and entity work."),
            ("Can any business benefit from GEO?", "If users search for information related to your product, category or expertise — yes. B2B, SaaS, professional services, healthcare, finance, education and niche e-commerce all benefit most, because AI-search users are research-heavy and high-intent."),
        ],
    },
}

SS_ICONS = {
    "seo": '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    "content": '<svg viewBox="0 0 24 24"><path d="M4 4h16v4H4zM4 12h10v4H4zM4 20h16"/></svg>',
    "social": '<svg viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 10.5l6.8-4M8.6 13.5l6.8 4"/></svg>',
    "lead": '<svg viewBox="0 0 24 24"><path d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z"/><path d="M10 10l4 4"/></svg>',
    "video": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9l5 3-5 3z"/></svg>',
    "strategy": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg>',
    "growth": '<svg viewBox="0 0 24 24"><path d="M3 17l6-6 4 4 8-8"/><path d="M17 7h4v4"/></svg>',
    "chat": '<svg viewBox="0 0 24 24"><path d="M21 12a8 8 0 1 1-3.5-6.6L21 5l-1 4.2A8 8 0 0 1 21 12z"/></svg>',
    "brand": '<svg viewBox="0 0 24 24"><path d="M9 3l3 5 5 1-4 4 1 6-5-3-5 3 1-6-4-4 5-1z"/></svg>',
    "data": '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>',
    "ppc": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "perf": '<svg viewBox="0 0 24 24"><path d="M3 20h18"/><rect x="5" y="12" width="3" height="7" rx="1"/><rect x="11" y="8" width="3" height="11" rx="1"/><rect x="17" y="4" width="3" height="15" rx="1"/></svg>',
    "app": '<svg viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2"/><circle cx="12" cy="18" r="1"/><path d="M10 6h4"/><path d="M9 10l3 3 3-3"/></svg>',
    "revenue": '<svg viewBox="0 0 24 24"><path d="M12 2v20"/><path d="M17 6H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H7"/></svg>',
}

HERO_ORBS = """  <span class="hero-orb-1" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2l2.8 7h7l-5.7 4.2 2.2 7.2L12 16.6l-6.3 3.8 2.2-7.2L2.2 9h7z"/></svg></span>
  <span class="hero-orb-2" aria-hidden="true"><svg viewBox="0 0 60 60"><path d="M30 4 C 48 6 56 18 56 30 C 56 44 46 56 30 56 C 14 56 4 44 4 30 C 4 18 12 6 30 4 Z"/></svg></span>
  <span class="hero-orb-3" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2C8 6 4 10 4 14c0 5 4 8 8 8s8-3 8-8c0-4-4-8-8-12z"/></svg></span>
  <span class="hero-orb-4" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/></svg></span>
"""

MARQUEE_ITEMS = ["Performance-First", "Data-Driven", "Results That Compound", "Human + AI", "ROI Over Vanity", "Transparent Dashboards", "15+ Years Experience"]

PLATFORM_SVG = {
    "fb": '<svg viewBox="0 0 48 48"><defs><linearGradient id="fbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5851DB"/><stop offset=".5" stop-color="#E1306C"/><stop offset="1" stop-color="#F77737"/></linearGradient></defs><rect x="4" y="4" width="40" height="40" rx="10" fill="url(#fbg)"/><path d="M28 24h4l1-5h-5v-3c0-1.5.5-2.5 2.5-2.5H33V9.2C32.5 9.1 31 9 29.3 9c-3.5 0-5.8 2.1-5.8 6v4H19v5h4.5v12h5V24z" fill="#fff"/></svg>',
    "ln": '<svg viewBox="0 0 48 48"><rect x="4" y="4" width="40" height="40" rx="10" fill="#0A66C2"/><path d="M17 19h-4v14h4V19zm-2-6a2.3 2.3 0 1 0 0 4.6 2.3 2.3 0 0 0 0-4.6zM36 33h-4v-7c0-1.8-.6-3-2.3-3-1.3 0-2 .9-2.3 1.7-.1.3-.1.7-.1 1.1V33h-4V19h4v2c.5-.8 1.5-2.2 3.8-2.2 2.8 0 4.9 1.8 4.9 5.8V33z" fill="#fff"/></svg>',
    "yt": '<svg viewBox="0 0 48 48"><rect x="4" y="10" width="40" height="28" rx="8" fill="#FF0000"/><path d="M20 17v14l12-7-12-7z" fill="#fff"/></svg>',
    "search": '<svg viewBox="0 0 48 48"><rect x="4" y="4" width="40" height="40" rx="10" fill="#4285F4"/><circle cx="22" cy="22" r="7" fill="none" stroke="#fff" stroke-width="3"/><path d="M27 27l7 7" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg>',
    "display": '<svg viewBox="0 0 48 48"><rect x="4" y="4" width="40" height="40" rx="10" fill="#FF6B6B"/><rect x="12" y="14" width="24" height="18" rx="2" fill="none" stroke="#fff" stroke-width="2.5"/><path d="M16 20h12M16 24h16M16 28h10" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>',
    "shopping": '<svg viewBox="0 0 48 48"><rect x="4" y="4" width="40" height="40" rx="10" fill="#FF9F43"/><path d="M13 17h22l-2.5 15a2 2 0 0 1-2 1.7H17.5a2 2 0 0 1-2-1.7L13 17z" fill="none" stroke="#fff" stroke-width="2.5"/><path d="M20 17v-3a4 4 0 0 1 8 0v3" fill="none" stroke="#fff" stroke-width="2.5"/></svg>',
    "remarket": '<svg viewBox="0 0 48 48"><rect x="4" y="4" width="40" height="40" rx="10" fill="#10B981"/><path d="M34 14a10 10 0 1 0 3 12" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/><path d="M34 10v6h-6" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "app": '<svg viewBox="0 0 48 48"><rect x="4" y="4" width="40" height="40" rx="10" fill="#8B5CF6"/><rect x="17" y="10" width="14" height="28" rx="2" fill="none" stroke="#fff" stroke-width="2.5"/><path d="M24 18v8m-3-3 3 3 3-3" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="24" cy="32" r="1.2" fill="#fff"/></svg>',
}

def svc_template(p):
    # Hero
    items = (p.get("marquee") or MARQUEE_ITEMS) * 3
    marquee_html = "".join(f'<span class="marquee-item">{m}</span>' for m in items)
    subtitle_html = f'<p class="hero-subtitle">{p["kicker"]}</p>' if p.get("kicker") else ""
    hero = f"""<section class="about-hero svc-hero">
{HERO_ORBS}  <div class="container">
    <div class="breadcrumb">{p["crumb"]}</div>
    <h1>{p["h1"]}</h1>
    {subtitle_html}
    <p class="lead">{p["intro"]}</p>
    <div class="hero-sub"><a class="btn" href="contact-us.html">Start Your Project</a></div>
  </div>
</section>
<section class="marquee-strip" aria-hidden="true">
  <div class="marquee-track">{marquee_html}</div>
</section>
"""

    # Split-panel helper (used by highlight, approach, best_campaigns, highlights[])
    def split_panel(data, extra_class="", extra_body=""):
        side = data.get("side", "right")
        side_cls = "right" if side == "right" else ""
        body_html = ""
        if "body" in data:
            body_html = f"<p>{data['body']}</p>"
        else:
            for key in ("body1", "body2", "body3"):
                if data.get(key): body_html += f"<p>{data[key]}</p>"
        intro_html = f"<p>{data['intro']}</p>" if data.get("intro") else ""
        bullets_html = ""
        if data.get("bullets"):
            items = "".join(f"<li><strong>{b[0]}:</strong> {b[1]}</li>" for b in data["bullets"])
            bullets_html = f"<ul class=\"split-bullets\">{items}</ul>"
        cta_html = f'<a class="btn" href="contact-us.html">{data["cta_text"]}</a>' if data.get("cta_text") else ""
        return f"""<section class="svc-split {side_cls} {extra_class}">
  <div class="container">
    <div class="svc-split-img reveal"><img src="{data['img']}" alt="" loading="lazy"></div>
    <div class="svc-split-copy reveal delay-1"><h2>{data['heading']}</h2>{body_html}{intro_html}{bullets_html}{extra_body}{cta_html}</div>
  </div>
</section>
"""
    # What Is section (optional)
    what_is_section = ""
    if p.get("what_is"):
        wh_head, wh_body = p["what_is"]
        what_is_section = f"""<section class="about-sec">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">The Basics</span><h2>{wh_head}</h2></div>
    <div class="svc-whatis-card reveal">{wh_body}</div>
  </div>
</section>
"""
    # Sub-services OR deliverables
    mid_section = ""
    if p.get("sub_services"):
        cards = "".join(
            f'<div class="sub-svc-card reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><div class="ss-icon">{SS_ICONS.get(ic, SS_ICONS["strategy"])}</div><div><h3>{t}</h3><p>{d}</p></div></div>'
            for i, (ic, t, d) in enumerate(p["sub_services"])
        )
        mid_section = f"""<section class="services-expertise" style="padding:90px 0">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Our Services</span><h2>What We <span class="green_text">Deliver</span></h2></div>
    <div class="sub-svc-grid">{cards}</div>
  </div>
</section>
"""
    elif p.get("deliverables"):
        deliver_tiles = "".join(
            f'<div class="svc-deliver reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><div class="dot"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>{d}</p></div>'
            for i, d in enumerate(p["deliverables"])
        )
        mid_section = f"""<section class="why-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Deliverables</span><h2>What's <span class="green_text">Included</span></h2></div>
    <div class="svc-deliver-grid">{deliver_tiles}</div>
  </div>
</section>
"""
    # Benefits — either numbered cards (2-tuple) or image cards (3-tuple)
    benefits = ""
    if p.get("benefits"):
        intro_html = f'<p>{p["benefits_intro"]}</p>' if p.get("benefits_intro") else ""
        # Detect shape: if first item has 3 elements, use image layout
        if len(p["benefits"][0]) == 3:
            cards = "".join(
                f'<div class="benefit-img-card reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><div class="bi-img" style="background-image:url({img})"></div><div class="bi-body"><h3>{t}</h3><p>{d}</p></div></div>'
                for i, (t, d, img) in enumerate(p["benefits"])
            )
            benefits = f"""<section class="about-sec values-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Why Work With Us</span><h2>Benefits Of Working With A <span class="green_text">Paid Social Media Agency</span></h2>{intro_html}</div>
    <div class="benefits-img-grid">{cards}</div>
  </div>
</section>
"""
        else:
            bene_icons = ["M3 20h18M5 12v7M11 8v11M17 4v15","M12 2a10 10 0 1 0 10 10M12 6v6l4 2","M13 2L5 14h6l-2 8 10-14h-6z","M12 21c5-4 9-9 9-14 0-2-1-3-3-3-3 0-4 3-6 3s-3-3-6-3c-2 0-3 1-3 3 0 5 4 10 9 14z","M20 6L9 17l-5-5","M12 2L15 8l6 1-4 4 1 6-6-3-6 3 1-6-4-4 6-1z"]
            bene_cards = "".join(
                f'<div class="value-card reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><span class="val-num">{(i+1):02d}</span><div class="val-icon"><svg viewBox="0 0 24 24"><path d="{bene_icons[i%len(bene_icons)]}"/></svg></div><h3>{t}</h3><p>{d}</p></div>'
                for i, (t, d) in enumerate(p["benefits"])
            )
            benefits = f"""<section class="about-sec values-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Why Choose DigiVeritaz</span><h2>Key <span class="green_text">Benefits</span></h2>{intro_html}</div>
    <div class="values-grid">{bene_cards}</div>
  </div>
</section>
"""

    # Optional highlight (why-matters) and approach split panels
    highlight_section = split_panel(p["highlight"]) if p.get("highlight") else ""
    approach_section = split_panel(p["approach"]) if p.get("approach") else ""

    # Multiple highlights (list of split-panels) — used when page has several image+text sections
    highlights_html = ""
    if p.get("highlights"):
        highlights_html = "".join(split_panel(h) for h in p["highlights"])

    # Packages / Tier cards
    packages_section = ""
    if p.get("packages"):
        pk = p["packages"]
        tier_html = "".join(
            f'<div class="pkg-card reveal{" featured" if featured else ""}{" delay-"+str(i) if i else ""}"><div class="pkg-header"><h3>{name}</h3><p>{profile}</p></div><div class="pkg-duration"><p class="dur">{duration}</p></div><div class="pkg-services"><div class="svc-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>{services}</p></div></div>'
            for i, (name, profile, duration, services, *rest) in enumerate(pk["tiers"])
            for featured in [rest[0] if rest else (i == 1)]  # default middle tier is featured
        )
        intro_html = f'<p>{pk["intro"]}</p>' if pk.get("intro") else ""
        packages_section = f"""<section class="packages-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Engagement Models</span><h2>{pk.get("heading", "Typical Engagements &amp; <span class=\"green_text\">Packages</span>")}</h2>{intro_html}</div>
    <div class="pkg-grid">{tier_html}</div>
  </div>
</section>
"""

    # Simple benefits — styled bulleted list in a card
    simple_benefits_section = ""
    if p.get("simple_benefits"):
        sb_head = p["simple_benefits"].get("heading", "Benefits")
        sb_items = "".join(f"<li>{item}</li>" for item in p["simple_benefits"]["items"])
        simple_benefits_section = f"""<section class="simple-benefits-wrap">
  <div class="container">
    <div class="simple-benefits reveal">
      <span class="kicker">What You Get</span>
      <h2>{sb_head}</h2>
      <ul>{sb_items}</ul>
    </div>
  </div>
</section>
"""

    # Platforms (3-card)
    platforms_section = ""
    if p.get("platforms"):
        cards = "".join(
            f'<div class="platform-card reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><div class="pf-logo">{PLATFORM_SVG.get(ic, PLATFORM_SVG["fb"])}</div><h3>{t}</h3><p>{d}</p></div>'
            for i, (ic, t, d) in enumerate(p["platforms"])
        )
        intro = f'<p>{p["platforms_intro"]}</p>' if p.get("platforms_intro") else ""
        outro = f'<div class="platforms-outro reveal">{p["platforms_outro"]}</div>' if p.get("platforms_outro") else ""
        platforms_section = f"""<section class="platforms-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Platforms</span><h2>Platforms We <span class="green_text">Specialize In</span></h2>{intro}</div>
    <div class="platforms-grid">{cards}</div>
    {outro}
  </div>
</section>
"""

    # Best campaigns (split panel with sub-heading)
    best_section = ""
    if p.get("best_campaigns"):
        bc = p["best_campaigns"]
        sub = f'<div class="best-sub"><h3>{bc["sub_heading"]}</h3><p>{bc["sub_body"]}</p></div>' if bc.get("sub_heading") else ""
        best_section = split_panel(bc, extra_class="best-campaigns", extra_body=sub)
    # Process — vertical editorial timeline (optional)
    process = ""
    if p.get("process"):
        tl_arrow_svg = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
        proc_steps = "".join(
            f'<div class="tl-step reveal"><div class="tl-marker"><div class="tl-num">{(i+1):02d}</div></div><span class="tl-arrow">{tl_arrow_svg}</span><div class="tl-content"><span class="tl-kicker">Step {(i+1):02d}</span><h3>{t}</h3><p>{d}</p></div></div>'
            for i, (t, d) in enumerate(p["process"])
        )
        process = f"""<section class="process-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Our Process</span><h2>How <span class="green_text">We Work</span></h2><p>A phased engagement, fully transparent — so you always know what's happening next.</p></div>
    <div class="process-timeline">{proc_steps}</div>
  </div>
</section>
"""
    # Industries (optional)
    industries_section = ""
    if p.get("industries"):
        pills = "".join(f'<span class="industry-pill">{ind}</span>' for ind in p["industries"])
        industries_section = f"""<section class="about-sec">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Who We Serve</span><h2>Industries We <span class="green_text">Serve</span></h2></div>
    <div class="industries-grid reveal">{pills}</div>
  </div>
</section>
"""
    # FAQs
    faqs_section = ""
    if p.get("faqs"):
        faq_html = "".join(
            f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>'
            for q, a in p["faqs"]
        )
        faqs_section = f"""<section class="about-sec">
  <div class="container svc-faq-wrap">
    <div class="sec-head reveal"><span class="kicker">FAQs</span><h2>Frequently Asked <span class="green_text">Questions</span></h2></div>
    {faq_html}
  </div>
</section>
"""
    # CTA
    cta_head, cta_body = p.get("cta", ("Ready to grow your <span>brand?</span>", "Book a free consultation and get a custom proposal within 48 hours."))
    cta = f"""<section class="about-cta">
  <div class="container reveal">
    <h2>{cta_head}</h2>
    <p>{cta_body}</p>
    <a class="btn" href="contact-us.html">Start Your Project</a>
  </div>
</section>
"""
    divider = '<div class="svc-divider" aria-hidden="true"></div>\n'
    parts = [hero]
    if what_is_section: parts += [what_is_section, divider]
    if highlights_html: parts.append(highlights_html)
    if mid_section: parts.append(mid_section)
    if highlight_section: parts.append(highlight_section)
    if approach_section: parts.append(approach_section)
    if process: parts.append(process)
    if platforms_section: parts.append(platforms_section)
    if benefits: parts.append(benefits)
    if simple_benefits_section: parts.append(simple_benefits_section)
    if packages_section: parts.append(packages_section)
    if best_section: parts.append(best_section)
    if industries_section: parts.append(industries_section)
    if faqs_section: parts.append(faqs_section)
    parts.append(cta)
    return "".join(parts)

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

SERVICE_KEYWORD_EXTRA = {
    "seo.html": "SEO services India, technical SEO, SEO agency Mumbai, local SEO, keyword research, link building",
    "pay-per-click.html": "PPC services India, Google Ads management, Bing Ads, pay per click agency Mumbai, Shopping Ads",
    "performance-marketing-agency.html": "performance marketing agency India, ROAS optimization, CAC reduction, full funnel marketing, ROI marketing",
    "paid-social-media-advertising.html": "paid social media advertising, Meta Ads, Facebook Ads, Instagram Ads, LinkedIn Ads, Pinterest Ads India",
    "ecommerce-marketing.html": "ecommerce marketing India, Amazon marketing, Flipkart ads, Shopify marketing, D2C growth, marketplace management",
    "whatsapp-marketing-services.html": "WhatsApp marketing India, WhatsApp Business API, bulk messaging, chatbot automation, conversational commerce",
    "native-advertising.html": "native advertising India, sponsored content, discovery ads, Swiggy ads, Zomato ads, Blinkit advertising",
    "organic-marketing-services.html": "organic marketing services, content marketing India, community building, SEO strategy, organic social",
    "branding-and-design.html": "branding and design services, brand strategy, identity design, creative direction, content design Mumbai",
    "generative-search-optimisation.html": "generative search optimization, GSO, GEO, AI search ranking, ChatGPT SEO, Gemini SEO, Perplexity visibility",
    "data-strategy-consulting-services.html": "data strategy consulting, GA4 setup, attribution modeling, analytics consulting, CDP integration",
}

# _strip_tags is defined later (in FAQ section); ensure it exists here by importing forward
import re as _pre_re
def _strip_tags(s): return _pre_re.sub(r'<[^>]+>','',s).replace('&amp;','&').strip()

for fname, p in service_pages.items():
    body = svc_template(p)
    kw = DEFAULT_KEYWORDS + ", " + SERVICE_KEYWORD_EXTRA.get(fname, "")
    sjsonld = service_jsonld(fname, p["title"], p["desc"], p.get("faqs"))
    write(fname, p["title"], p["desc"], body, keywords=kw, extra_jsonld=sjsonld)

# ---------- CASE STUDY ----------
# (slug, title, tag, description, image)
case_items = [
    ("hyundai-pledge-to-be-safe", "Hyundai &mdash; Pledge to Be Safe", "Automotive",
     "A nationwide road-safety campaign that turned a social message into 34.6M+ reach and 15.2M+ video views.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/hyundai.jpg"),
    ("khyber-cement-cementing-regional-awareness-through-digital-visibility", "Khyber Cement", "Manufacturing",
     "Cementing regional awareness across J&amp;K and North India with two TVCs &mdash; 13.9M+ impressions, 9M+ views.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/khyber.jpg"),
    ("jk-shah-classes-quality-leads", "JK Shah Classes &mdash; Quality Leads", "Education",
     "1,500+ leads with 80% marked high-quality via a full-funnel Meta + Google performance engine.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/jk-shah.jpg"),
    ("my-bid-app-multi-platform-growth", "MY BID App &mdash; Multi-Platform Growth", "App Growth",
     "3,400+ successful registrations across Meta, Google Search, Display and Programmatic.",
     "https://digiveritaz.com/wp-content/uploads/2025/10/mybid-1.png"),
    ("shiamak-one-year-program-stepping-up-digital-engagement-for-aspiring-dancers", "Shiamak &mdash; Stepping Up Digital Engagement", "Arts &amp; Education",
     "A friction-free, mobile-first system that reached aspiring dancers across 12+ cities.",
     "https://digiveritaz.com/wp-content/uploads/2025/10/Shamak-OYP.png"),
    ("ebco-forging-digital-success-with-integrated-campaigns", "EBCO &mdash; Integrated Digital Success", "D2C / Industrial",
     "12M+ impressions, 100K+ clicks and 2.34x ROAS for a legacy hardware leader.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/ebco.jpg"),
    ("hyundai-elite-i20-lead-generation-campaign", "Hyundai Elite i20 &mdash; Lead Generation", "Automotive",
     "5,000+ quality leads for the premium hatchback from 3.3M+ Meta impressions.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/hyundai.jpg"),
    ("transcon-triumph-building-leads-visibility-through-multi-platform-campaigns", "Transcon &mdash; Leads &amp; Visibility", "Real Estate",
     "289 leads + 300K+ YouTube views at a 64.08% view-through rate for a premium residential launch.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/transcon-Triumph.jpg"),
    ("legal-junction-building-a-long-term-lead-engine-for-rent-agreement-services", "Legal Junction &mdash; Long-Term Lead Engine", "Legal Services",
     "450+ quality leads at 7% conversion and &#8377;450 CPL via Google Search + WhatsApp automation.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/legal-Junction.jpg"),
    ("seo-case-study-themauve-co", "TheMauve.co &mdash; SEO Case Study", "E-commerce &middot; SEO",
     "Technical SEO, content clusters and internal linking that lifted organic traffic for a D2C fashion brand.",
     "https://digiveritaz.com/wp-content/uploads/2025/10/Ashton-Cro.webp"),
    ("seo-case-study-mayapuri-com", "Mayapuri.com &mdash; SEO Case Study", "Publishing &middot; SEO",
     "A structured SEO + Google Discover programme that grew non-brand organic for Bollywood news.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/jk-shah.jpg"),
    ("case-study-gy3-fashion-sales-branding", "GY3 &mdash; Fashion, Sales &amp; Branding", "Fashion &amp; Retail",
     "PPC rebuilt as a long-term sales + branding engine &mdash; improved ROAS, stronger brand visibility.",
     "https://digiveritaz.com/wp-content/uploads/2025/10/Shamak-OYP.png"),
    ("ppc-case-study-tulsi-realty-9-meraki-panvel-lead-generation", "Tulsi Realty &mdash; 9 Meraki Panvel", "Real Estate &middot; PPC",
     "Geo-targeted Google Search delivering site-visit-ready homebuyers in Panvel.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/transcon-Triumph.jpg"),
    ("zedex-mobility-car-booking-campaigns", "Zedex Mobility &mdash; Car Bookings at Scale", "Automotive",
     "81 avg. bookings/month across Tata, Kia and &Scaron;koda &mdash; with up to 200X peak-season ROAS.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/hyundai.jpg"),
    ("stem-rx-regenerative-hospital-marketing", "Stem RX &mdash; Regenerative Hospital", "Healthcare",
     "&#8377;142 CPL with 90% OTP-verified lead quality and 35&ndash;45% organic growth.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/ebco.jpg"),
    ("shape-u-clinic-aesthetic-lead-generation", "Shape U Clinic &mdash; 1,556 Leads / Month", "Aesthetics",
     "A precision Meta funnel with WhatsApp automation generating 1,556 qualified treatment leads per month.",
     "https://digiveritaz.com/wp-content/uploads/2025/10/Ashton-Cro.webp"),
    ("siws-school-admissions-ppc", "SIWS &mdash; Admissions Engine", "Education",
     "300 leads at &#8377;131 CPL with +65% social engagement growth for a Mumbai K&ndash;12 school.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/jk-shah.jpg"),
    ("rawood-sheed-timber-lead-generation", "RaWood Sheed &mdash; Niche B2B Demand", "Timber",
     "600 product inquiries/month at &#8377;50 CPI and 3X ROAS in a niche live-edge timber market.",
     "https://digiveritaz.com/wp-content/uploads/2025/06/ebco.jpg"),
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
      "Real results from DigiVeritaz clients — Hyundai, JK Shah, Khyber Cement, EBCO, MY BID and more. See case studies across education, D2C, real estate, automotive and F&amp;B.",
      cs_body,
      keywords=DEFAULT_KEYWORDS + ", digital marketing case studies, marketing success stories, Hyundai case study, JK Shah case study, Mumbai agency portfolio")

# ---------- BLOG ----------
blog_posts = [
    ("The 2026 Guide to Generative Search Optimization", "Learn how to rank in ChatGPT, Gemini and Perplexity as AI reshapes discovery."),
    ("Why Performance Marketing Needs Brand", "The CAC spiral is real — here's how brand investment lowers your blended cost per acquisition."),
    ("WhatsApp Commerce Is the Next Growth Channel", "Why Indian D2C brands are shifting retention budgets to conversational channels."),
    ("Amazon Ads: 7 Tactics That Still Work in 2026", "Proven tactics our team uses to drive ROAS on India's largest marketplace."),
    ("Attribution Is Broken. Here's What We Do Instead", "Move beyond last-click with incrementality testing and MMM-lite frameworks."),
    ("Creative Testing at Scale", "How to design a creative testing engine that produces winners week after week."),
]
blog_cards = "".join(
    f'<a class="card" href="#"><div class="thumb" style="background-image:url(\'https://images.unsplash.com/photo-{i}?auto=format&fit=crop&w=800&q=80\')"></div><div class="body"><span class="tag">Insights</span><h3>{t}</h3><p>{d}</p></div></a>'
    for i,(t,d) in zip(["1432888622747-4eb9a8efeb07","1460925895917-afdab827c52f","1551288049-bebda4e38f71","1556761175-5973dc0f32e7","1552664730-d307ca884978","1542744173-8e7e53415bb0"], blog_posts)
)
blog_body = page_hero("Blog &amp; <span class=\"green_text\">Insights</span>", "Home / Blog",
    "Tactical playbooks, industry trends and behind-the-scenes from our team.") + f"""
<section><div class="container"><div class="card-grid">{blog_cards}</div></div></section>
"""
write("blog.html",
      "Digital Marketing Blog &amp; Insights | DigiVeritaz",
      "Digital marketing playbooks, SEO tips, PPC strategies and growth insights from the DigiVeritaz team. Learn what works in 2026 and beyond.",
      blog_body,
      keywords=DEFAULT_KEYWORDS + ", digital marketing blog, SEO tips, PPC tips, marketing insights India, growth marketing blog")

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
      "FAQ | DigiVeritaz — Digital Marketing Agency Questions Answered",
      "Frequently asked questions about DigiVeritaz — services, engagement models, pricing, reporting and how we measure ROI for digital marketing campaigns.",
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
<h2>6. Your Rights</h2><p>You may request access to, correction of, or deletion of your personal data at any time by emailing mihir@digiveritaz.com.</p>
<h2>7. Data Sharing</h2><p>We do not sell your data. We share it only with trusted service providers who help us operate our business, under strict confidentiality.</p>
<h2>8. Security</h2><p>We implement industry-standard safeguards to protect your data, though no method of transmission over the Internet is 100% secure.</p>
<h2>9. External Links</h2><p>Our site may contain links to external sites whose privacy practices we do not control.</p>
<h2>10. Marketing Opt-Out</h2><p>You can opt out of marketing communications at any time by using the unsubscribe link in our emails.</p>
<h2>11. Contact</h2><p>Privacy Officer: Mihir Lunia · mihir@digiveritaz.com · +91 99566 55662 · Ujagar Chambers, Deonar, Chembur, Mumbai 400088.</p>
<h2>12. Updates</h2><p>We may update this policy from time to time. Material changes will be communicated via our website.</p>
</div></section>
"""
write("privacy-policy.html",
      "Privacy Policy | DigiVeritaz",
      "DigiVeritaz privacy policy — how we collect, use, and protect your personal information.",
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
      "Terms &amp; Conditions | DigiVeritaz",
      "DigiVeritaz terms and conditions governing the use of our services and engagements.",
      terms_body,
      keywords="terms and conditions, service agreement, DigiVeritaz terms")

print("Built pages:")
for f in sorted(OUT.glob("*.html")):
    print(" -", f.name)
