#!/usr/bin/env python3
"""Static page builder for DigiVeritaz recreation.
Generates all HTML pages from shared header/footer + per-page content blocks.
"""
import os, pathlib

OUT = pathlib.Path(__file__).parent

NAV_ITEMS = [
    ("index.html", "Home"),
    ("about-us.html", "About Us"),
    ("services.html", "Services"),
    ("case-study.html", "Case Study"),
    ("blog.html", "Blog"),
    ("contact-us.html", "Contact Us"),
]

def build_nav(current):
    # mark active: direct match, or services.html active for any service sub-page
    def is_active(href):
        if href == current: return True
        if href == "services.html" and current not in {i[0] for i in NAV_ITEMS} and current.endswith(".html"):
            service_slugs = {"seo.html","pay-per-click.html","performance-marketing-agency.html","paid-social-media-advertising.html","ecommerce-marketing.html","whatsapp-marketing-services.html","native-advertising.html","organic-marketing-services.html","branding-and-design.html","generative-search-optimisation.html","data-strategy-consulting-services.html"}
            return current in service_slugs
        return False
    lis = "\n      ".join(
        f'<li><a class="navlink{" active" if is_active(h) else ""}" href="{h}">{t}</a></li>'
        for h,t in NAV_ITEMS
    )
    return f"""    <ul>
      {lis}
      <li class="cta"><a class="btn" href="contact-us.html">Book A Call</a></li>
    </ul>"""

HEAD_TPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<header class="site-header">
  <div class="container nav">
    <a class="brand" href="index.html">
      <img src="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp" alt="DigiVeritaz">
      <b>Digi</b><span>Veritaz</span>
    </a>
    <button class="hamb" aria-label="Menu">&#9776;</button>
{nav}
  </div>
</header>
"""

FOOT = """<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="foot-brand" href="index.html">
          <img src="https://digiveritaz.com/wp-content/uploads/2025/12/3D1.webp" alt="DigiVeritaz">
          <b>Digi</b><span>Veritaz</span>
        </a>
        <div class="foot-socials">
          <a href="#" aria-label="Facebook"><svg viewBox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H8v-3h2.4V9.4c0-2.4 1.4-3.7 3.6-3.7 1 0 2.1.2 2.1.2v2.3h-1.2c-1.2 0-1.5.7-1.5 1.5V12h2.6l-.4 3h-2.2v7A10 10 0 0 0 22 12z"/></svg></a>
          <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.3 2.2.4.6.2 1 .5 1.5 1s.8.9 1 1.5c.1.4.3 1 .4 2.2.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.3 1.8-.4 2.2-.2.6-.5 1-1 1.5s-.9.8-1.5 1c-.4.1-1 .3-2.2.4-1.2.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.3-2.2-.4-.6-.2-1-.5-1.5-1s-.8-.9-1-1.5c-.1-.4-.3-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.3-1.8.4-2.2.2-.6.5-1 1-1.5s.9-.8 1.5-1c.4-.1 1-.3 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.7.1-1.1.1-1.7.2-2.1.4-.5.2-.9.4-1.3.8s-.6.8-.8 1.3c-.2.4-.3 1-.4 2.1-.1 1.2-.1 1.6-.1 4.7s0 3.5.1 4.7c.1 1.1.2 1.7.4 2.1.2.5.4.9.8 1.3s.8.6 1.3.8c.4.2 1 .3 2.1.4 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c1.1-.1 1.7-.2 2.1-.4.5-.2.9-.4 1.3-.8s.6-.8.8-1.3c.2-.4.3-1 .4-2.1.1-1.2.1-1.6.1-4.7s0-3.5-.1-4.7c-.1-1.1-.2-1.7-.4-2.1-.2-.5-.4-.9-.8-1.3s-.8-.6-1.3-.8c-.4-.2-1-.3-2.1-.4-1.2-.1-1.6-.1-4.7-.1zm0 3.1a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8zm0 8.1a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4zm6.3-8.3a1.1 1.1 0 1 1-2.3 0 1.1 1.1 0 0 1 2.3 0z"/></svg></a>
          <a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24"><path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2zM8 19H5V9h3v10zM6.5 7.7a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4zM19 19h-3v-5.3c0-1.3 0-2.9-1.8-2.9s-2 1.4-2 2.8V19h-3V9h2.9v1.4h0a3.2 3.2 0 0 1 2.9-1.6c3.1 0 3.7 2 3.7 4.7V19z"/></svg></a>
        </div>
        <p class="foot-copy">© Copyright 2026 DigiVeritaz.<br>All rights reserved.</p>
      </div>

      <div>
        <h4>Our Services</h4>
        <div class="foot-services">
          <ul>
            <li><a href="organic-marketing-services.html">Organic Marketing Services</a></li>
            <li><a href="paid-social-media-advertising.html">Paid Social Media Advertising</a></li>
            <li><a href="pay-per-click.html">Pay Per Click</a></li>
            <li><a href="performance-marketing-agency.html">Performance Marketing Agency</a></li>
          </ul>
          <ul>
            <li><a href="ecommerce-marketing.html">E-Commerce Platforms</a></li>
            <li><a href="data-strategy-consulting-services.html">Data Strategy &amp; Consulting</a></li>
            <li><a href="native-advertising.html">Native Advertising</a></li>
            <li><a href="whatsapp-marketing-services.html">WhatsApp Marketing Services</a></li>
          </ul>
          <ul>
            <li><a href="branding-and-design.html">Branding and Design</a></li>
            <li><a href="seo.html">Search Engine Optimization</a></li>
            <li><a href="generative-search-optimisation.html">Generative Search Optimisation</a></li>
          </ul>
        </div>
      </div>

      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about-us.html">Who We Are</a></li>
          <li><a href="services.html">What We Do</a></li>
          <li><a href="services.html">Our Service Expertise</a></li>
          <li><a href="case-study.html">Our Partnerships</a></li>
          <li><a href="blog.html">Blog</a></li>
          <li><a href="contact-us.html">Contact Us</a></li>
        </ul>
      </div>
    </div>

    <div class="foot-bottom">
      <a href="faq.html">FAQ</a>
      <a href="privacy-policy.html">Privacy Policy</a>
      <a href="terms-and-conditions.html">Terms and Conditions</a>
    </div>
  </div>
</footer>

<button class="to-top" aria-label="Back to top"><svg viewBox="0 0 24 24"><path d="M6 15l6-6 6 6"/></svg></button>

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

def write(name, title, desc, body):
    head = HEAD_TPL.format(title=title, desc=desc, nav=build_nav(name))
    (OUT / name).write_text(head + body + FOOT)

# ---------- ABOUT ----------
about_body = page_hero(
    "About <span class=\"green_text\">DigiVeritaz</span>",
    "Home / About Us",
    "We are a performance-first digital marketing agency headquartered in Mumbai, partnering with brands across India and beyond to deliver measurable growth."
) + """
<section>
  <div class="container grid-2">
    <div>
      <h2>Our <span class="green_text">Story</span></h2>
      <p>DigiVeritaz was founded on a simple belief — marketing should be accountable. In a world where vanity metrics often drown out what really matters, we built an agency that obsesses over ROI, customer lifetime value, and real business outcomes.</p>
      <p>Today, our team of 65+ seasoned specialists combines startup agility with enterprise-grade experience, delivering full-funnel campaigns across search, social, performance, and brand.</p>
    </div>
    <div><img src="https://digiveritaz.com/wp-content/uploads/2025/07/2-2-scaled.jpg" onerror="this.src='https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=900&q=80'" alt="Our team" style="border-radius:20px;box-shadow:var(--shadow)"></div>
  </div>
</section>

<section class="services">
  <div class="container">
    <div class="section-head"><h2>What Drives <span class="green_text">Us</span></h2></div>
    <div class="services-grid">
      <div class="svc-card"><div class="icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg></div><h3>Performance First</h3><p>Every campaign is measured, optimized, and tied to KPIs that matter — CPA, ROAS, LTV.</p></div>
      <div class="svc-card"><div class="icon"><svg viewBox="0 0 24 24"><path d="M12 3a5 5 0 0 0-5 5v1a4 4 0 0 0-2 7 4 4 0 0 0 7 3 4 4 0 0 0 7-3 4 4 0 0 0-2-7V8a5 5 0 0 0-5-5z"/></svg></div><h3>Data-Led Strategy</h3><p>We let numbers shape decisions, not assumptions. From attribution to incrementality.</p></div>
      <div class="svc-card"><div class="icon"><svg viewBox="0 0 24 24"><path d="M13 2L5 14h6l-2 8 10-14h-6z"/></svg></div><h3>Creative Muscle</h3><p>Performance is amplified by strong creative. Our team builds thumb-stopping work that converts.</p></div>
      <div class="svc-card"><div class="icon"><svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.2"/><circle cx="17" cy="9" r="2.6"/><path d="M3 19c0-3 2.7-5 6-5s6 2 6 5"/><path d="M14 18c0-2.4 2-4 4.5-4s2.5 1.6 2.5 4"/></svg></div><h3>Partnership Mindset</h3><p>We embed with your team and treat your goals as our own. No silos, no surprises.</p></div>
      <div class="svc-card"><div class="icon"><svg viewBox="0 0 24 24"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg></div><h3>Startup Agility</h3><p>Enterprise experience with the speed of a startup — we ship, learn, and iterate fast.</p></div>
      <div class="svc-card"><div class="icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/></svg></div><h3>Global Reach</h3><p>13+ global partnerships spanning 7 industries, from education to automotive to D2C.</p></div>
    </div>
  </div>
</section>

<section class="stats">
  <div class="container">
    <div><h3>60<span>+</span></h3><p>Clients served</p></div>
    <div><h3>13<span>+</span></h3><p>Global partners</p></div>
    <div><h3>65<span>+</span></h3><p>Years combined experience</p></div>
    <div><h3>1.15L<span>+</span></h3><p>Qualified leads delivered</p></div>
    <div><h3>4–10<span>x</span></h3><p>Average ROI</p></div>
  </div>
</section>
"""
write("about-us.html", "About Us | DigiVeritaz", "Learn about DigiVeritaz — a Mumbai-based digital marketing agency delivering performance-first growth.", about_body)

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
write("contact-us.html", "Contact Us | DigiVeritaz", "Get in touch with DigiVeritaz for a free digital marketing proposal.", contact_body)

# ---------- THANK YOU ----------
ty_body = """<section class="hero"><div class="container text-center">
<h1 class="play">Thank <span class="green_text">You!</span></h1>
<p class="lead" style="margin:0 auto">We've received your message and will get back to you shortly. If your inquiry is urgent, please call us directly at +91 9930070767.</p>
<div class="mt-20"><a class="btn" href="index.html">Back to Home</a></div>
</div></section>"""
write("thank-you.html", "Thank You | DigiVeritaz", "Thank you for contacting DigiVeritaz.", ty_body)

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
write("services.html", "Services | DigiVeritaz", "Explore DigiVeritaz services: SEO, PPC, performance marketing, e-commerce, branding and more.", svc_body)

# ---------- INDIVIDUAL SERVICE PAGES ----------
service_pages = {
    "seo.html": {
        "title": "SEO Services | DigiVeritaz",
        "desc": "Enterprise-grade SEO services — technical SEO, content, and link building that grow organic revenue.",
        "h1": "SEO Services That <span class=\"green_text\">Grow Revenue</span>",
        "crumb": "Home / Services / SEO",
        "intro": "We engineer organic growth through technical audits, content strategy, and trustworthy link building.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/marketing.jpg",
        "points": ["Technical SEO audits &amp; Core Web Vitals","Keyword research &amp; content strategy","On-page optimization","Authority link building","Local &amp; international SEO","Reporting with business KPIs"],
    },
    "pay-per-click.html": {
        "title": "Pay Per Click (PPC) | DigiVeritaz",
        "desc": "PPC services that drive high-intent traffic and ROI-positive conversions.",
        "h1": "Pay-Per-Click <span class=\"green_text\">Advertising</span>",
        "crumb": "Home / Services / Pay Per Click",
        "intro": "Get in front of buyers the moment they're searching — with Google Ads, Bing Ads and Shopping campaigns built for ROI.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/ppc-Advertising.jpg",
        "points": ["Google Search &amp; Display","Shopping &amp; Performance Max","Remarketing funnels","Bid strategy &amp; budget pacing","Landing page CRO","Weekly performance reviews"],
    },
    "performance-marketing-agency.html": {
        "title": "Performance Marketing Agency | DigiVeritaz",
        "desc": "Full-funnel performance marketing across search, display, shopping and video.",
        "h1": "Performance <span class=\"green_text\">Marketing</span>",
        "crumb": "Home / Services / Performance Marketing",
        "intro": "Smart funnels, smarter conversions. We blend creative, media, and analytics to hit your CAC and ROAS targets.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/performance-Marketing.jpg",
        "points": ["Cross-channel media planning","Attribution &amp; incrementality","Creative testing at scale","Funnel &amp; CRO optimization","Automated reporting","Dedicated growth team"],
    },
    "paid-social-media-advertising.html": {
        "title": "Paid Social Media Advertising | DigiVeritaz",
        "desc": "Facebook, Instagram, LinkedIn, Pinterest and Snapchat advertising that drives measurable outcomes.",
        "h1": "Paid Social <span class=\"green_text\">Advertising</span>",
        "crumb": "Home / Services / Paid Social",
        "intro": "From Meta to LinkedIn, we turn ad spend into profitable growth with creative that stops the scroll.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/ads-desktop.jpg",
        "points": ["Meta Ads (Facebook &amp; Instagram)","LinkedIn B2B campaigns","Pinterest &amp; Snapchat","Creative production","Audience building &amp; lookalikes","Conversion API integration"],
    },
    "ecommerce-marketing.html": {
        "title": "E-Commerce Marketing Services | DigiVeritaz",
        "desc": "Managed e-commerce marketing across Amazon, Flipkart, Shopify and D2C.",
        "h1": "E-Commerce <span class=\"green_text\">Marketing</span>",
        "crumb": "Home / Services / E-Commerce",
        "intro": "End-to-end Amazon, Flipkart and D2C growth — from listings and ads to conversion optimization.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/ecommerce-Platforms-1.jpg",
        "points": ["Amazon Ads &amp; SEO","Flipkart &amp; Myntra management","Shopify growth","CRO &amp; A/B testing","Retention &amp; loyalty","Marketplace analytics"],
    },
    "whatsapp-marketing-services.html": {
        "title": "WhatsApp Marketing Services | DigiVeritaz",
        "desc": "WhatsApp Business API marketing, automation and bulk messaging.",
        "h1": "WhatsApp <span class=\"green_text\">Marketing</span>",
        "crumb": "Home / Services / WhatsApp Marketing",
        "intro": "Direct, personal, conversational — WhatsApp is the highest-converting channel you're underusing.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/10/WhatsApp-Marketing.jpg",
        "points": ["WhatsApp Business API setup","Bulk messaging &amp; broadcasts","Chatbot automation","Campaign management","Catalogue &amp; commerce","CRM integration"],
    },
    "native-advertising.html": {
        "title": "Native Advertising Services | DigiVeritaz",
        "desc": "Premium native advertising placements that drive brand awareness and engagement.",
        "h1": "Native <span class=\"green_text\">Advertising</span>",
        "crumb": "Home / Services / Native Advertising",
        "intro": "Reach audiences on Amazon, Flipkart, Swiggy, Zomato, Blinkit, Zepto, Myntra and premium publishers.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/whats-app-Desktop.jpg",
        "points": ["Premium publisher placements","Marketplace native ads","Branded content","Sponsored discovery","Performance tracking","Programmatic buying"],
    },
    "organic-marketing-services.html": {
        "title": "Organic Marketing Services | DigiVeritaz",
        "desc": "Long-term organic growth via SEO, social and content.",
        "h1": "Organic <span class=\"green_text\">Marketing</span>",
        "crumb": "Home / Services / Organic Marketing",
        "intro": "Sustainable growth built on earned audiences — search, social and content working together.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/marketing.jpg",
        "points": ["SEO &amp; content","Organic social strategy","Community building","Influencer partnerships","PR &amp; outreach","Brand monitoring"],
    },
    "branding-and-design.html": {
        "title": "Branding and Design Services | DigiVeritaz",
        "desc": "Brand strategy, identity and design systems that convert.",
        "h1": "Branding &amp; <span class=\"green_text\">Design</span>",
        "crumb": "Home / Services / Branding &amp; Design",
        "intro": "A strong brand is your best sales tool. We build identity systems that scale across every touchpoint.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/branding-and-Design.jpg",
        "points": ["Brand research &amp; insights","Strategy &amp; positioning","Identity &amp; visual systems","Content &amp; copywriting","Audits &amp; analytics","Creative direction"],
    },
    "generative-search-optimisation.html": {
        "title": "Generative Search Optimisation (GSO) | DigiVeritaz",
        "desc": "Get discovered in ChatGPT, Gemini, Perplexity and AI-powered search.",
        "h1": "Generative Search <span class=\"green_text\">Optimisation</span>",
        "crumb": "Home / Services / GSO",
        "intro": "The future of search is AI. We help your brand surface in ChatGPT, Gemini, Perplexity and Google AI Overviews.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/marketing.jpg",
        "points": ["AI search visibility audits","Entity &amp; schema optimization","Content for LLMs","Brand authority signals","Citation building","GSO analytics &amp; tracking"],
    },
    "data-strategy-consulting-services.html": {
        "title": "Data Strategy &amp; Consulting | DigiVeritaz",
        "desc": "Data strategy, attribution and analytics consulting for growth-stage brands.",
        "h1": "Data Strategy &amp; <span class=\"green_text\">Consulting</span>",
        "crumb": "Home / Services / Data Strategy",
        "intro": "Know what's working, what isn't, and what to do next — with a measurement stack built for growth decisions.",
        "img": "https://digiveritaz.com/wp-content/uploads/2025/06/data-Strategy-and-Consulting.jpg",
        "points": ["Analytics &amp; GA4 setup","Server-side tracking","Attribution modeling","Dashboards &amp; reporting","Data warehousing","CDP &amp; CRM integration"],
    },
}

def svc_template(h1, crumb, intro, img, points):
    bullets = "".join(f"<li>{p}</li>" for p in points)
    return page_hero(h1, crumb, intro) + f"""
<section><div class="container grid-2">
  <div><img src="{img}" onerror="this.src='https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80'" alt="" style="border-radius:20px;box-shadow:var(--shadow)"></div>
  <div>
    <h2>What's <span class="green_text">Included</span></h2>
    <ul class="list-check">{bullets}</ul>
    <div class="mt-20"><a class="btn" href="contact-us.html">Get a Proposal</a></div>
  </div>
</div></section>

<section class="services"><div class="container">
  <div class="section-head"><h2>Our <span class="green_text">Process</span></h2></div>
  <div class="services-grid">
    <div class="svc-card"><div class="icon">1</div><h3>Discover</h3><p>We audit your current state, goals, and competitors to shape a custom strategy.</p></div>
    <div class="svc-card"><div class="icon">2</div><h3>Plan</h3><p>Channel mix, budget allocation, creative brief and KPI framework — all aligned.</p></div>
    <div class="svc-card"><div class="icon">3</div><h3>Launch</h3><p>We ship campaigns, instrument tracking, and start collecting signal from day one.</p></div>
    <div class="svc-card"><div class="icon">4</div><h3>Optimize</h3><p>Weekly testing, creative rotation and bid adjustments to push CAC down and ROAS up.</p></div>
    <div class="svc-card"><div class="icon">5</div><h3>Report</h3><p>Transparent dashboards, business-metric reporting and strategic reviews.</p></div>
    <div class="svc-card"><div class="icon">6</div><h3>Scale</h3><p>Once unit economics are proven, we unlock new markets and budgets with confidence.</p></div>
  </div>
</div></section>
"""

for fname, p in service_pages.items():
    body = svc_template(p["h1"], p["crumb"], p["intro"], p["img"], p["points"])
    write(fname, p["title"], p["desc"], body)

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
write("case-study.html", "Case Studies | DigiVeritaz", "Explore DigiVeritaz case studies across education, D2C, real estate, automotive and more.", cs_body)

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
write("blog.html", "Blog | DigiVeritaz", "Marketing insights, playbooks and case studies from the DigiVeritaz team.", blog_body)

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
write("faq.html", "FAQ | DigiVeritaz", "Frequently asked questions about DigiVeritaz services, process and engagement models.", faq_body)

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
write("privacy-policy.html", "Privacy Policy | DigiVeritaz", "DigiVeritaz privacy policy.", privacy_body)

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
write("terms-and-conditions.html", "Terms &amp; Conditions | DigiVeritaz", "DigiVeritaz terms and conditions.", terms_body)

print("Built pages:")
for f in sorted(OUT.glob("*.html")):
    print(" -", f.name)
