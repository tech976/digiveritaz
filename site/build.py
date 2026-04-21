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

def build_nav(current):
    # mark active: direct match, or services.html active for any service sub-page
    def is_active(href):
        if href == current: return True
        if href == "services.html" and current not in {i[0] for i in NAV_ITEMS} and current.endswith(".html"):
            service_slugs = {"seo.html","pay-per-click.html","performance-marketing-agency.html","paid-social-media-advertising.html","ecommerce-marketing.html","whatsapp-marketing-services.html","native-advertising.html","organic-marketing-services.html","branding-and-design.html","generative-search-optimisation.html","data-strategy-consulting-services.html"}
            return current in service_slugs
        return False
    lis = "\n      ".join(
        f'<li><a class="navlink{" active" if is_active(h) else ""}" href="{h}" data-i18n="{k}">{t}</a></li>'
        for h,t,k in NAV_ITEMS
    )
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
            "telephone": "+91-9930070767",
            "email": "info@digiveritaz.com",
            "priceRange": "$$",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "1st Floor, Office 06, Raghuvanshi Mansion, Raghuvanshi Mill Compound, Senapati Bapat Marg, Lower Parel",
                "addressLocality": "Mumbai",
                "addressRegion": "Maharashtra",
                "postalCode": "400013",
                "addressCountry": "IN"
            },
            "geo": {"@type":"GeoCoordinates","latitude":19.0078,"longitude":72.8309},
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
<link rel="stylesheet" href="css/style.css">

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
            <a href="#" aria-label="Facebook"><svg viewBox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H8v-3h2.4V9.4c0-2.4 1.4-3.7 3.6-3.7 1 0 2.1.2 2.1.2v2.3h-1.2c-1.2 0-1.5.7-1.5 1.5V12h2.6l-.4 3h-2.2v7A10 10 0 0 0 22 12z"/></svg></a>
            <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.3 2.2.4.6.2 1 .5 1.5 1s.8.9 1 1.5c.1.4.3 1 .4 2.2.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.3 1.8-.4 2.2-.2.6-.5 1-1 1.5s-.9.8-1.5 1c-.4.1-1 .3-2.2.4-1.2.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.3-2.2-.4-.6-.2-1-.5-1.5-1s-.8-.9-1-1.5c-.1-.4-.3-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.3-1.8.4-2.2.2-.6.5-1 1-1.5s.9-.8 1.5-1c.4-.1 1-.3 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 8.1a3.2 3.2 0 1 0 0 6.4 3.2 3.2 0 0 0 0-6.4zm6.3-8.3a1.1 1.1 0 1 1-2.3 0 1.1 1.1 0 0 1 2.3 0z"/></svg></a>
            <a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24"><path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2zM8 19H5V9h3v10zM6.5 7.7a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4zM19 19h-3v-5.3c0-1.3 0-2.9-1.8-2.9s-2 1.4-2 2.8V19h-3V9h2.9v1.4h0a3.2 3.2 0 0 1 2.9-1.6c3.1 0 3.7 2 3.7 4.7V19z"/></svg></a>
            <a href="#" aria-label="X / Twitter"><svg viewBox="0 0 24 24"><path d="M18.9 2H22l-7.5 8.6L23.5 22h-6.9l-5.4-7-6.2 7H2l8-9.2L1.7 2h7l4.9 6.5z"/></svg></a>
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
            <div><strong>Mumbai HQ</strong>Raghuvanshi Mansion, Lower Parel, Mumbai 400013</div>
          </div>
          <div class="foot-contact-row">
            <span class="ic"><svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2z"/></svg></span>
            <div><strong>Phone</strong>+91 99300 70767</div>
          </div>
          <div class="foot-contact-row">
            <span class="ic"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg></span>
            <div><strong>Email</strong>info@digiveritaz.com</div>
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

<script src="js/i18n.js"></script>
<script src="js/main.js"></script>
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

def write(name, title, desc, body, keywords=None, extra_jsonld=""):
    kw = keywords or DEFAULT_KEYWORDS
    canonical = name.replace("index.html","") if name == "index.html" else name.replace(".html","/")
    crumb = breadcrumb_jsonld(name, title)
    head = HEAD_TPL.format(
        title=title, desc=desc, keywords=kw, canonical=canonical,
        nav="{nav}", extra_jsonld=(crumb + extra_jsonld),
    )
    head = head.replace("{nav}", build_nav(name))
    main = '\n<main id="main" role="main">\n'
    closemain = '\n</main>\n'
    (OUT / name).write_text(head + main + body + closemain + FOOT)

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
contact_body = page_hero(
    "Let's <span class=\"green_text\">Talk Growth</span>",
    "Home / Contact Us",
    "Tell us about your goals and we'll respond within one business day with a tailored plan."
) + """
<section>
  <div class="container" style="display:grid;grid-template-columns:1.2fr .8fr;gap:40px">
    <form id="contact-form" novalidate>
      <div class="field"><label>Full Name</label><input type="text" name="fullname" placeholder="Your full name"><div class="error_frm" id="error_fname"></div></div>
      <div class="field"><label>Email Address</label><input type="email" name="email" placeholder="you@company.com"><div class="error_frm" id="error_email"></div></div>
      <div class="field"><label>Phone Number</label><input type="tel" name="phone" placeholder="+91 9XXXXXXXXX"><div class="error_frm" id="error_phone"></div></div>
      <div class="field"><label>Company Name</label><input type="text" name="company" placeholder="Company"></div>
      <div class="field">
        <label>Budget Range</label>
        <select name="budget">
          <option>-- Please select budget range --</option>
          <option>INR 40k - 60k</option>
          <option>INR 60k to 1 Lac</option>
          <option>INR 1 Lac and above</option>
        </select>
      </div>
      <div class="field">
        <label>Select the Services You Need</label>
        <div class="check-grid">
          <label><input type="checkbox" name="svc" value="Organic Marketing"> Organic Marketing</label>
          <label><input type="checkbox" name="svc" value="Paid Social Media"> Paid Social Media Advertising</label>
          <label><input type="checkbox" name="svc" value="PPC"> Pay-Per-Click Advertising</label>
          <label><input type="checkbox" name="svc" value="Performance Marketing"> Performance Marketing</label>
          <label><input type="checkbox" name="svc" value="E-commerce"> E-commerce Platforms</label>
          <label><input type="checkbox" name="svc" value="Data Strategy"> Data Strategy and Consulting</label>
          <label><input type="checkbox" name="svc" value="Native Advertising"> Native Advertising</label>
          <label><input type="checkbox" name="svc" value="WhatsApp"> WhatsApp Marketing</label>
          <label><input type="checkbox" name="svc" value="Branding"> Branding and Design</label>
          <label><input type="checkbox" name="svc" value="SEO"> Search Engine Optimization</label>
          <label><input type="checkbox" name="svc" value="GSO"> Generative Search Optimisation</label>
        </div>
      </div>
      <div class="field"><label>Project Brief</label><textarea name="message" rows="5" placeholder="Brief your tentative start date, goals, platforms of interest, reference brands, etc."></textarea></div>
      <button class="btn" type="submit">Send Request</button>
    </form>
    <aside>
      <div class="tcard">
        <h3>Get in touch</h3>
        <p><strong>Mumbai HQ</strong><br>1st Floor, Office No. 06<br>Raghuvanshi Mansion, Raghuvanshi Mill Compound<br>Senapati Bapat Marg, Lower Parel<br>Mumbai – 400013</p>
        <p><strong>Phone</strong><br>+91 9930070767<br>+91 9956655662</p>
        <p><strong>Email</strong><br>info@digiveritaz.com<br>mihir@digiveritaz.com</p>
      </div>
    </aside>
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
      "Contact DigiVeritaz for a free digital marketing proposal. Call +91 99300 70767 or email info@digiveritaz.com. Based in Mumbai, serving clients across India and globally.",
      contact_body,
      keywords=DEFAULT_KEYWORDS + ", contact digital marketing agency, marketing agency Mumbai contact, free marketing proposal, digital marketing consultation",
      extra_jsonld=contact_jsonld)

# ---------- THANK YOU ----------
ty_body = """<section class="hero"><div class="container text-center">
<h1 class="play">Thank <span class="green_text">You!</span></h1>
<p class="lead" style="margin:0 auto">We've received your message and will get back to you shortly. If your inquiry is urgent, please call us directly at +91 9930070767.</p>
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
        "desc": "Drive sustainable growth without paid ads. SEO, content marketing, social media optimization and analytics that build long-term audiences and compounding ROI.",
        "h1": "Drive Sustainable Growth Without <span class=\"green_text\">Paid Ads</span>",
        "crumb": "Home / Services / Organic Marketing",
        "kicker": "Organic Marketing",
        "intro": "We help brands expand naturally using SEO, content marketing, social media optimization and analytics — instead of relying solely on paid advertisements.",
        "benefits": [
            ("Long-Term Brand Authority", "Compounding credibility as organic presence builds trust over time."),
            ("Lower Acquisition Costs", "Reduced dependency on paid media means healthier unit economics."),
            ("Consistent Website Traffic", "A steady pipeline of qualified visitors — not rented attention."),
            ("Improved SEO Rankings", "Higher visibility across search, video and social surfaces."),
            ("Quality Organic Leads", "Visitors who arrive through intent convert better and stay longer."),
            ("Audience Loyalty", "Earned audiences stick around — and advocate for your brand."),
        ],
        "deliverables": [
            "Organic SEO (keyword research, on-page, backlinks)",
            "Content Marketing (blogs, infographics, videos)",
            "Social Media Organic Marketing (posting, storytelling, engagement)",
            "Organic Lead Generation (optimized funnels)",
            "YouTube &amp; Video Optimization",
        ],
        "process": [
            ("Audit &amp; Strategy Building", "Evaluate website and competition to shape the plan."),
            ("Keyword Mapping &amp; Content Planning", "Identify high-volume, low-difficulty keywords and content pillars."),
            ("On-Page SEO Optimization", "Improve meta tags, structure and user experience."),
            ("Content Creation &amp; Distribution", "Blogs, landing pages, and social posts built for reach."),
            ("Engagement &amp; Outreach", "Build trust through organic engagement and community."),
            ("Tracking &amp; Reporting", "Monitor analytics for traffic, engagement and ROI."),
        ],
        "faqs": [],
    },
    "paid-social-media-advertising.html": {
        "title": "Paid Social Media Advertising | Meta, LinkedIn, YouTube Ads | DigiVeritaz",
        "desc": "Paid social media advertising that drives real ROI. Facebook, Instagram, LinkedIn and YouTube campaigns blending video-led creative with precise targeting and retargeting funnels.",
        "h1": "Paid Social <span class=\"green_text\">Advertising</span>",
        "crumb": "Home / Services / Paid Social",
        "kicker": "Paid Social Advertising",
        "intro": "In today's competitive landscape, organic reach alone isn't enough. Paid advertising on social media lets you connect with the right audience, at the right time, with precision targeting — and creative that stops the scroll.",
        "benefits": [
            ("Wider Reach &amp; Visibility", "Go beyond existing followers and reach new qualified audiences."),
            ("Faster Results", "Immediate visibility and conversions versus slower organic growth."),
            ("Precise Targeting", "Demographic, behavioral and intent-based audience layers."),
            ("Budget Flexibility", "Start small, test, and scale what works."),
            ("Higher Engagement", "Creative formats — video, carousel, story — drive interaction."),
            ("Remarketing &amp; Data Insights", "Retarget warm audiences and refine strategy with rich data."),
        ],
        "deliverables": [
            "Facebook &amp; Instagram (Meta) Ads",
            "LinkedIn Ads (B2B targeting)",
            "YouTube &amp; Video Ads",
            "Creative production (video-led)",
            "Audience building &amp; lookalikes",
            "Retargeting funnels &amp; Conversion API setup",
        ],
        "process": [
            ("Audience &amp; Goals Research", "Understand buyer personas and campaign objectives."),
            ("Creative Development", "Video-led ad concepts, storyboards and production."),
            ("Campaign Launch &amp; Monitoring", "Ship, instrument and start collecting signal from day one."),
            ("Continuous Optimization", "Adjust targeting, bidding and creatives weekly for ROI."),
        ],
        "faqs": [
            ("What is paid advertising on social media?", "Targeted paid campaigns on platforms like Facebook, Instagram, LinkedIn and YouTube — delivering faster results for leads, sales, or brand awareness than organic alone."),
            ("How does paid differ from organic posts?", "Paid campaigns guarantee visibility through targeting and budget, while organic posts rely on algorithmic reach that's declined significantly across platforms."),
            ("Which platforms work best?", "Facebook/Instagram for broad reach and direct response; LinkedIn for B2B; YouTube for storytelling and consideration."),
            ("What's the recommended budget?", "Campaigns typically start from ₹20,000/month. Focus should be on ROI and unit economics over absolute spend."),
            ("How do you measure success?", "Impressions, clicks, conversions, cost per lead, and return on ad spend — reported in a transparent dashboard."),
        ],
    },
    "pay-per-click.html": {
        "title": "PPC Agency in India | Google Ads Management | DigiVeritaz",
        "desc": "Pay-Per-Click advertising that turns clicks into customers. End-to-end Google Ads, Shopping, Display and Video campaigns with full-funnel tracking, CRO and ROI-focused optimization.",
        "h1": "Drive Instant Visibility and Conversions with <span class=\"green_text\">PPC</span>",
        "crumb": "Home / Services / Pay Per Click",
        "kicker": "Pay-Per-Click (PPC)",
        "intro": "PPC turns clicks into customers — not just traffic. We serve startups through established businesses with measurable, ROI-focused campaign management across Google, Shopping and Display.",
        "benefits": [
            ("Immediate Top-of-SERP Presence", "Appear where buyers are searching the moment you launch."),
            ("Controlled Budgeting", "Pay only on clicks or conversions — full cost control."),
            ("Precise Targeting", "Location, device, keyword and behavior-level targeting."),
            ("Measurable Outcomes", "Track CPC, CTR, CPA, ROAS and Quality Score in real time."),
            ("Rapid Experimentation", "Test ad copies, landing pages and bidding strategies at speed."),
            ("Scalable Growth", "Double down on ROI-positive campaigns with confidence."),
        ],
        "deliverables": [
            "Strategy &amp; Planning",
            "Campaign Setup (Google Ads, Display, Shopping, Video)",
            "Creative Development (copy, banners, A/B testing)",
            "Landing Page &amp; Conversion Optimization",
            "Bid Management &amp; Budget Allocation",
            "Ongoing Optimization, Tracking &amp; Reporting",
        ],
        "process": [
            ("Discovery &amp; Audit", "Business goals, competitors and existing campaign assessment."),
            ("Keyword &amp; Market Research", "Uncover profitable keywords, trends and seasonality."),
            ("Strategy &amp; Campaign Architecture", "Structure accounts by objective, theme and funnel stage."),
            ("Ad Copy, Creative &amp; Extensions", "Compelling copy, visuals, video and ad extensions."),
            ("Tracking &amp; Infrastructure", "Conversion tracking, GA4 and server-side setup."),
            ("Launch &amp; Monitor", "Dial in bids, pacing and early-signal optimization."),
            ("Optimization &amp; Scaling", "Refine keywords, test creatives and scale winners."),
        ],
        "faqs": [
            ("What is PPC campaign management?", "The end-to-end process of planning, launching, monitoring, optimizing and scaling paid campaigns. Expert management prevents wasted spend on irrelevant clicks and poor targeting."),
            ("How soon will I see results?", "Initial results appear immediately; meaningful conversions and stable ROAS typically take 2–4 weeks of optimization cycles."),
            ("Which keywords should we target?", "Intent-driven keywords and long-tail variants (e.g. 'buy shoes online'). We avoid generic queries with low conversion intent."),
            ("How is success measured?", "CPC, CTR, CPA, conversion rate, ROAS, Quality Score and impression share — shown in transparent dashboards, not cherry-picked screenshots."),
        ],
    },
    "performance-marketing-agency.html": {
        "title": "Performance Marketing Agency in India &amp; Mumbai | DigiVeritaz",
        "desc": "Performance marketing agency delivering measurable growth across search, social, display and app. Full-funnel CRO, lead gen, media buying and ROI-focused optimization.",
        "h1": "Driving Measurable Growth with <span class=\"green_text\">Performance Marketing</span>",
        "crumb": "Home / Services / Performance Marketing",
        "kicker": "Performance Marketing",
        "intro": "In a crowded digital marketplace, you need more than visibility — you need performance. Our performance marketing agency in Mumbai delivers results tied to CPL, CPA and ROAS, not vanity metrics.",
        "benefits": [
            ("Revenue-Driven Campaigns", "Every channel tied to CPL, CPA and ROAS targets."),
            ("Data-First Approach", "Decisions backed by attribution and tested hypotheses."),
            ("Full-Funnel Optimization", "TOFU awareness through MOFU nurture to BOFU conversion."),
            ("Cross-Channel Synergy", "Coordinated media buys across search, social, display, video."),
            ("Agile &amp; Transparent Execution", "Weekly sprints and open dashboards — no black boxes."),
            ("Dedicated Growth Team", "A specialist pod: strategist, media buyer, creative, analyst."),
        ],
        "deliverables": [
            "Paid Media (Search, Social, Display)",
            "Conversion Rate Optimization (CRO)",
            "Lead Generation Specialist Support",
            "App Installs &amp; Mobile Marketing",
            "Social Media Performance Boost",
            "Transparent Pricing &amp; ROI Forecasts",
        ],
        "process": [
            ("Discovery &amp; Audit", "Current-state analysis of accounts, funnels and tracking."),
            ("Strategy Planning", "Channel mix, budget allocation and KPI framework."),
            ("Creative &amp; Copy Development", "Performance creative built to test and scale."),
            ("Execution &amp; Media Buying", "Ship campaigns with proper instrumentation."),
            ("CRO Service", "Landing page optimization and funnel experiments."),
            ("Tracking, Analytics &amp; Reporting", "Dashboards, attribution, and weekly insights."),
            ("Iterative Optimization", "Weekly test cycles — kill losers, scale winners."),
        ],
        "faqs": [
            ("How is performance marketing different from traditional digital marketing?", "Traditional digital marketing often optimizes for awareness, traffic and followers. Performance marketing ties every rupee of spend to measurable outcomes — leads, purchases, revenue."),
            ("What's the realistic timeline to see ROI?", "Initial testing takes 2–4 weeks; significant compounding results typically appear in 8–12 weeks as optimization cycles mature."),
            ("Is there a minimum budget?", "It depends on industry, competition and channel mix. We customize based on expected outcomes — and won't take on accounts where spend can't meet CAC targets."),
            ("Is this full-service?", "Yes — creative, media buying, CRO, analytics and reporting are all handled end-to-end by the same pod."),
            ("Which industries do you serve?", "E-commerce, SaaS, startups, apps, retail, education, hospitality and local businesses across India and overseas."),
        ],
    },
    "ecommerce-marketing.html": {
        "title": "E-Commerce Managed Services | Amazon, Flipkart, Shopify | DigiVeritaz",
        "desc": "E-commerce platforms managed services that scale your online business across Amazon, Flipkart, Shopify and D2C. Listings, ads, fulfillment, analytics and growth.",
        "h1": "Managed Services That Scale Your <span class=\"green_text\">Online Business</span>",
        "crumb": "Home / Services / E-Commerce",
        "kicker": "E-Commerce Platforms",
        "intro": "We partner with you to thrive. Our e-commerce management services empower brands to compete, convert and scale across marketplaces and independent webstores — with the analytics and operational rigor your board expects.",
        "benefits": [
            ("End-to-End Capability", "Platform, product, ads and operations under one roof."),
            ("White-Label Operations", "Your brand, our operations — no service gaps."),
            ("Data-Driven Decisions", "Sales, margin and inventory insights informing every move."),
            ("Scalable for Any Size", "From launch to enterprise — the model flexes."),
            ("Compliance &amp; Risk Mitigation", "Marketplace policy, returns and disputes handled."),
            ("Dedicated Account Management", "A named lead accountable for growth and SLAs."),
        ],
        "deliverables": [
            "Platform &amp; marketplace setup with optimization",
            "Product &amp; catalog management with SEO",
            "Order, inventory and fulfillment oversight",
            "E-commerce advertising (Amazon Ads, Sponsored Products, Meta Shops)",
            "Custom analytics dashboards (sales, AOV, ROAS, ACOS)",
            "Returns, reviews and marketplace compliance",
        ],
        "process": [
            ("Discovery &amp; Audit", "Evaluate existing presence and map to business goals."),
            ("Strategic Roadmap", "Propose platforms, priorities and tech stack."),
            ("Implementation &amp; Setup", "Deploy platforms, configure dashboards, integrate partners."),
            ("Launch &amp; Go-Live Support", "Optimize store, monitor real-time, fix issues."),
            ("Ongoing Management &amp; Growth", "Account management, campaigns, optimization and scaling."),
        ],
        "faqs": [
            ("What does 'e-commerce managed service' include?", "End-to-end support: platform setup, product &amp; inventory management, order fulfilment, returns/logistics, ad campaigns, analytics, compliance and ongoing optimization."),
            ("What is a white-label e-commerce platform?", "A store branded as yours with your logo and design, while the backend operations and tech are handled by our team."),
            ("Which KPIs do you track?", "Conversion rate, AOV, repeat purchase rate, return rate, ROAS/ACOS, inventory turnover, gross margin and customer lifetime value."),
            ("Can you manage both marketplaces and standalone stores?", "Yes — we cover Amazon, Flipkart and independent platforms like Shopify and WooCommerce."),
            ("How quickly do we see results?", "Setup takes 1–2 weeks; early traffic in weeks; sustainable performance typically in 3–6 months."),
        ],
    },
    "data-strategy-consulting-services.html": {
        "title": "Data Strategy &amp; Consulting Services | Analytics, GA4 &amp; Dashboards | DigiVeritaz",
        "desc": "Data strategy and consulting for growth-stage brands — GA4 setup, attribution, dashboards (Looker, Power BI, Tableau) and measurement frameworks that drive decisions.",
        "h1": "Data Strategy &amp; <span class=\"green_text\">Consulting</span>",
        "crumb": "Home / Services / Data Strategy",
        "kicker": "Data Strategy &amp; Consulting",
        "intro": "In an environment overflowing with data, what matters is extracting real insight — and using it to fuel growth. Our Data Strategy &amp; Consulting service is designed exactly for that purpose.",
        "benefits": [
            ("Aligned Business Objectives", "KPIs and metrics tied directly to business goals."),
            ("Trustworthy Reporting", "Consistency and accuracy across every data source."),
            ("Scalable Frameworks", "Measurement that evolves with your market and scale."),
            ("Competitive Advantage", "Faster insights and trend prediction than your competitors."),
            ("Higher Marketing ROI", "Spend decisions backed by real measurement, not instinct."),
            ("Cross-Team Alignment", "Unified definitions mean everyone's optimizing the same thing."),
        ],
        "deliverables": [
            "Data pipeline setup &amp; platform integration",
            "Dashboards in GA4, Looker Studio, Power BI, Tableau",
            "KPI definition and governance policies",
            "Content strategy shaped by performance insights",
            "Regular reporting and trend analysis meetings",
            "Team training on data literacy and dashboard interpretation",
        ],
        "process": [
            ("Discovery Call", "Understand business challenges and data sources."),
            ("Audit of Current State", "Review existing tools, dashboards and tracking."),
            ("Strategy Workshop", "Define goals, metrics and an implementation roadmap."),
            ("Implementation Phase", "Set up tracking, dashboards and data integrations."),
            ("Insight &amp; Analytics Phase", "Regular reporting and trend analysis meetings."),
            ("Optimization &amp; Scaling", "Iterate, introduce advanced analytics, refine."),
            ("Training &amp; Transition", "Build internal team capability to sustain."),
        ],
        "faqs": [
            ("How long does implementation take?", "For SMEs, a complete audit, roadmap and initial setup usually takes 6–10 weeks. For large enterprises with multiple departments, it can extend to a few months."),
            ("Which tools do you use?", "Google Analytics (GA4), Looker Studio, Power BI and Tableau — plus CRM integrations and ETL tools when needed."),
            ("Is this only for large companies?", "No — the approach scales for startups, SMEs and enterprises alike."),
            ("Can you train internal teams?", "Yes — we provide workshops and hands-on training on data literacy, dashboard reading and content strategy."),
            ("What ROI should we expect?", "Stronger spend-to-conversion alignment, improved decision efficiency and reduced campaign wastage."),
        ],
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
        "faqs": [],
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
        "faqs": [],
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
        "faqs": [],
    },
}

def svc_template(p):
    # Hero
    hero = f"""<section class="about-hero">
  <div class="container">
    <div class="breadcrumb">{p["crumb"]}</div>
    <span class="kicker">{p["kicker"]}</span>
    <h1>{p["h1"]}</h1>
    <p class="lead">{p["intro"]}</p>
    <div class="hero-sub"><a class="btn" href="contact-us.html">Book A Free Consultation</a></div>
  </div>
</section>
"""
    # Benefits
    bene_icons = ["M3 20h18M5 12v7M11 8v11M17 4v15","M12 2a10 10 0 1 0 10 10M12 6v6l4 2","M13 2L5 14h6l-2 8 10-14h-6z","M12 21c5-4 9-9 9-14 0-2-1-3-3-3-3 0-4 3-6 3s-3-3-6-3c-2 0-3 1-3 3 0 5 4 10 9 14z","M20 6L9 17l-5-5","M12 2L15 8l6 1-4 4 1 6-6-3-6 3 1-6-4-4 6-1z"]
    bene_cards = "".join(
        f'<div class="value-card reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><span class="val-num">{(i+1):02d}</span><div class="val-icon"><svg viewBox="0 0 24 24"><path d="{bene_icons[i%len(bene_icons)]}"/></svg></div><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(p["benefits"])
    )
    benefits = f"""<section class="about-sec values-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Why Choose Us</span><h2>Key <span class="green_text">Benefits</span></h2></div>
    <div class="values-grid">{bene_cards}</div>
  </div>
</section>
"""
    # Deliverables
    deliver_tiles = "".join(
        f'<div class="svc-deliver reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><div class="dot"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div><p>{d}</p></div>'
        for i, d in enumerate(p["deliverables"])
    )
    deliverables = f"""<section class="why-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Deliverables</span><h2>What's <span class="green_text">Included</span></h2></div>
    <div class="svc-deliver-grid">{deliver_tiles}</div>
  </div>
</section>
"""
    # Process
    proc_cards = "".join(
        f'<div class="phase-card reveal{" delay-"+str((i%3)+1) if i%3 else ""}"><div class="phase-badge">{(i+1):02d}</div><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(p["process"])
    )
    process = f"""<section class="process-section">
  <div class="container">
    <div class="sec-head reveal"><span class="kicker">Our Process</span><h2>How <span class="green_text">We Work</span></h2></div>
    <div class="process-track auto">{proc_cards}</div>
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
    cta = """<section class="about-cta">
  <div class="container reveal">
    <h2>Ready to grow your <span>brand?</span></h2>
    <p>Book a free consultation and get a custom proposal within 48 hours.</p>
    <a class="btn" href="contact-us.html">Start Your Project</a>
  </div>
</section>
"""
    return hero + benefits + deliverables + process + faqs_section + cta

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
case_items = [
    ("Shiamak One Year Program", "Education", "Stepping up digital engagement for aspiring dancers across 12 cities.", "https://digiveritaz.com/wp-content/uploads/2025/10/Shamak-OYP.png"),
    ("EBCO", "D2C", "Forging digital success with integrated performance + brand campaigns.", "https://digiveritaz.com/wp-content/uploads/2025/06/ebco.jpg"),
    ("MY BID App", "App Growth", "Multi-platform growth that drove 5x installs and halved CPA.", "https://digiveritaz.com/wp-content/uploads/2025/10/mybid-1.png"),
    ("Hyundai India", "Automotive", "Regional demand campaigns that boosted showroom footfalls.", "https://digiveritaz.com/wp-content/uploads/2025/06/hyundai.jpg"),
    ("JK Shah Classes", "Education", "Lead generation engine producing thousands of qualified enquiries.", "https://digiveritaz.com/wp-content/uploads/2025/06/jk-shah.jpg"),
    ("Khyber Restaurants", "F&amp;B", "Brand &amp; social campaigns that filled seats and strengthened loyalty.", "https://digiveritaz.com/wp-content/uploads/2025/06/khyber.jpg"),
    ("Legal Junction", "Services", "Authority building through content and SEO for a legal-tech platform.", "https://digiveritaz.com/wp-content/uploads/2025/06/legal-Junction.jpg"),
    ("Transcon Triumph", "Real Estate", "High-intent lead generation for a premium real-estate launch.", "https://digiveritaz.com/wp-content/uploads/2025/06/transcon-Triumph.jpg"),
    ("Ashton Cro", "Retail", "Performance creative and CRO that improved store-level conversion.", "https://digiveritaz.com/wp-content/uploads/2025/10/Ashton-Cro.webp"),
]
case_cards = "".join(
    f'<a class="card" href="#"><div class="thumb" style="background-image:url(\'{img}\')"></div><div class="body"><span class="tag">{tag}</span><h3>{t}</h3><p>{d}</p></div></a>'
    for (t,tag,d,img) in case_items
)
cs_body = page_hero("Case <span class=\"green_text\">Studies</span>", "Home / Case Studies",
    "Real brands, real numbers. Explore how we've delivered measurable growth across industries.") + f"""
<section><div class="container"><div class="card-grid">{case_cards}</div></div></section>
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
    ("Where are you based?", "Our HQ is in Lower Parel, Mumbai, and we work with clients across India and overseas."),
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
<h2>11. Contact</h2><p>Privacy Officer: Mihir Lunia · mihir@digiveritaz.com · +91 9930070767 · Raghuvanshi Mansion, Lower Parel, Mumbai 400013.</p>
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
