#!/usr/bin/env python3
"""Title & description plan -> seo/data/meta_plan.json

Transcribed from "Title and Description - DigiVeritaz.xlsx - Final Title &
Description.pdf" (47 rows). The workbook itself could not be shared, so each
cell is checked against the character count the sheet states for it: if a
transcription and its stated length disagree, the row is reported rather than
trusted. Nothing here is applied to the site -- this only builds the data.

Page names are mapped to real sitemap URLs, never to the URLs printed in the
PDF: line wrapping there ate the hyphens ("social-mediamanagement").

Usage:  python3 build_meta_plan.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# (page name, site path, rec title, stated len, rec description, stated len,
#  primary keyword, secondary keyword)
ROWS = [
 ("Home", "/",
  "Top Digital marketing agency in India | DigiVeritaz Mumbai", 58,
  "DigiVeritaz is a 360-degree digital marketing agency in Mumbai delivering SEO, PPC, branding, and growth strategies for measurable business success every time.", 159,
  "Digital marketing agency in India", "360 Degree Digital Marketing Agency"),
 ("Services", "/services/",
  "Digital marketing services in India | DigiVeritaz India", 55,
  "DigiVeritaz delivers end-to-end digital marketing solutions across SEO, PPC, performance marketing, paid social, WhatsApp marketing, and branding every time.", 157,
  "Digital marketing services", "Digital Marketing Solutions"),
 ("SEO", "/services/seo/",
  "Leading SEO services for Businesses | DigiVeritaz India", 55,
  "DigiVeritaz is a trusted SEO agency Mumbai businesses rely on for technical fixes, content, and link building that drive lasting Page-1 rankings every time.", 156,
  "SEO services", "SEO agency Mumbai"),
 ("Social Media Management", "/services/social-media-management/",
  "Social media marketing agency in India | DigiVeritaz India", 58,
  "DigiVeritaz offers social media management services across Instagram, LinkedIn, and YouTube, planning, creating, and growing engagement for brands every time.", 158,
  "Social media marketing agency", "Social media management services"),
 ("Influencer Marketing", "/services/influencer-marketing/",
  "Influencer marketing agency in India | DigiVeritaz India", 56,
  "DigiVeritaz delivers influencer marketing services with 2,500+ vetted, ASCI-compliant creators for real, measurable reach across every platform every time.", 155,
  "Influencer marketing agency", "Influencer marketing services"),
 ("Digital PR", "/services/digital-pr/",
  "Digital PR services for Businesses | DigiVeritaz Mumbai", 55,
  "DigiVeritaz is a leading online PR agency, securing tier-1 editorial coverage and DA 70+ backlinks for ambitious Indian brands across every sector, every time.", 159,
  "Digital PR services", "Online PR agency"),
 ("Online Reputation Management", "/services/online-reputation-management/",
  "Online reputation management services | DigiVeritaz India", 57,
  "DigiVeritaz is a trusted ORM company that suppresses negatives, builds genuine reviews and protects your brand across Google and AI search results every time.", 158,
  "Online reputation management services", "ORM company"),
 ("Whatsapp Marketing", "/services/whatsapp-marketing/",
  "WhatsApp marketing services in India | DigiVeritaz India", 56,
  "DigiVeritaz is a WhatsApp marketing agency delivering Business API campaigns, broadcast flows, chatbots and 90%+ open rates for growing brands built to perform.", 160,
  "WhatsApp marketing services", "WhatsApp marketing agency"),
 ("Performance Marketing Agency", "/services/performance-marketing-agency/",
  "Performance marketing agency in India | DigiVeritaz India", 57,
  "DigiVeritaz is a Performance marketing company managing Rs 40Cr+ ad spend at a 4.6x blended ROAS across Google, Meta and full-funnel campaigns built to perform.", 160,
  "Performance marketing agency", "Performance marketing company"),
 ("Ecommerce Marketing", "/services/ecommerce-marketing/",
  "Ecommerce marketing agency in India | DigiVeritaz India", 55,
  "DigiVeritaz offers Ecommerce marketing services that scaled 60+ D2C stores to a 4.2x blended ROAS across Meta, Google and Shopify partnerships built to perform.", 160,
  "Ecommerce marketing agency", "Ecommerce marketing services"),
 ("Generative Search Optimisation", "/services/generative-search-optimisation/",
  "Best GEO agency for Generative Search Results | DigiVeritaz", 59,
  "DigiVeritaz specializes in Generative engine optimization, helping Indian brands get cited in ChatGPT, Gemini and Google AI Overviews consistently every time.", 158,
  "GEO agency", "Generative engine optimization"),
 ("Pay Per Click", "/services/pay-per-click/",
  "Top PPC agency for PPC Campaigns in India | DigiVeritaz", 55,
  "DigiVeritaz offers PPC management services with Rs 40Cr+ ad spend managed across India at an average 5.8x return on ad spend for every client with real results.", 160,
  "PPC agency", "PPC management services"),
 ("Display Advertising", "/services/display-advertising/",
  "Display advertising agency in India | DigiVeritaz India", 55,
  "DigiVeritaz offers Display advertising services across GDN, programmatic and retargeting campaigns built to deliver a strong 4-10x return on ad spend today.", 156,
  "Display advertising agency", "Display advertising services"),
 ("Facebook Instagram Advertising", "/services/facebook-instagram-advertising/",
  "Facebook advertising agency in India | DigiVeritaz India", 56,
  "DigiVeritaz is an Instagram advertising agency and Meta Business Partner delivering CAPI tracking and a proven 4.2x blended ROAS for every campaign every time.", 159,
  "Facebook advertising agency", "Instagram advertising agency"),
 ("Shopping Ads", "/services/shopping-ads/",
  "Google Shopping ads agency in India | DigiVeritaz India", 55,
  "DigiVeritaz offers Google Shopping management services that scaled 50k+ SKUs to a 5.6x average return on ad spend for ecommerce brands across India every time.", 159,
  "Google Shopping ads agency", "Google Shopping management services"),
 ("Paid Social Media Advertising", "/services/paid-social-media-advertising/",
  "Paid social media agency for Brands | DigiVeritaz India", 55,
  "DigiVeritaz delivers Paid social advertising services managing Rs 38Cr+ across Meta, LinkedIn, TikTok and YouTube with results tied to revenue built to perform.", 160,
  "Paid social media agency", "Paid social advertising services"),
 ("Amazon Marketing", "/services/amazon-marketing/",
  "Amazon marketing agency for Brands | DigiVeritaz Mumbai", 55,
  "DigiVeritaz is a certified Amazon advertising agency that scaled 500+ SKUs with Rs 40Cr+ in managed Amazon Ads spend for sellers across India with real results.", 160,
  "Amazon marketing agency", "Amazon advertising agency"),
 ("Native Advertising", "/services/native-advertising/",
  "Native advertising agency in India | DigiVeritaz Mumbai", 55,
  "DigiVeritaz offers Native advertising services with 240+ Outbrain and Taboola campaigns delivering a strong 1.1% average CTR for every brand with real results.", 159,
  "Native advertising agency", "Native advertising services"),
 ("Ui/Ux Design", "/services/ui-ux-design/",
  "UI UX design agency for Businesses | DigiVeritaz Mumbai", 55,
  "DigiVeritaz offers UI UX design services that shipped 100+ products across 50+ design systems, all Figma-native and WCAG AA compliant for every client today.", 157,
  "UI UX design agency", "UI UX design services"),
 ("Product Design", "/services/product-design/",
  "Product design services for Brands | DigiVeritaz Mumbai", 55,
  "DigiVeritaz specializes in Digital product design, shipping 100+ products and launching 25+ MVPs for SaaS and fintech founders across India with real results.", 158,
  "Product design services", "Digital product design"),
 ("Branding and Design", "/services/branding-and-design/",
  "Best Branding agency for Businesses | DigiVeritaz India", 55,
  "DigiVeritaz offers Branding services that shipped 200+ identities with strategy-led positioning and logo systems for ambitious brands across India every time.", 158,
  "Branding agency", "Branding services"),
 ("Communication Design", "/services/communication-design/",
  "Communication design agency in India | DigiVeritaz India", 56,
  "DigiVeritaz offers Communication design services — pitch decks, brochures, social templates and sales collateral that communicate your brand clearly every time.", 160,
  "Communication design agency", "Communication design services"),
 ("Content Copy Writing", "/services/content-copy-writing/",
  "Copywriting services for Businesses | DigiVeritaz India", 55,
  "DigiVeritaz is a Content marketing agency writing SEO articles, sales copy and email sequences that convert readers into paying customers with real results.", 156,
  "Copywriting services", "Content marketing agency"),
 ("Conversion Rate Optimisation", "/services/conversion-rate-optimisation/",
  "Leading CRO services for Businesses | DigiVeritaz India", 55,
  "DigiVeritaz offers Conversion optimization services that ran 200+ experiments for an average 32% CVR lift across client websites and landing pages every time.", 158,
  "CRO services", "Conversion optimization services"),
 ("Revenue Generation", "/services/revenue-generation/",
  "Revenue generation services in India | DigiVeritaz India", 56,
  "DigiVeritaz offers Business growth services that drove Rs 500Cr+ in pipeline through full-funnel attribution and a CRM-native revenue engine with real results.", 159,
  "Revenue generation services", "Business growth services"),
 ("Lead Generation", "/services/lead-generation/",
  "Lead generation agency for Businesses | DigiVeritaz India", 57,
  "DigiVeritaz offers Lead generation services that delivered 1M+ qualified leads with a 38% cut in cost per lead for B2B and B2C brands alike with real results.", 158,
  "Lead generation agency", "Lead generation services"),
 ("Cmo Consultancy", "/services/cmo-consultancy/",
  "Fractional CMO services for Brands | DigiVeritaz Mumbai", 55,
  "DigiVeritaz is a Marketing consultancy offering fractional leadership that has shaped Rs 1000Cr+ in budgets for founders and fast-scaling startups every time.", 158,
  "Fractional CMO services", "Marketing consultancy"),
 ("Landing Page Design", "/services/landing-page-design/",
  "Landing page design agency in India | DigiVeritaz India", 55,
  "DigiVeritaz offers Landing page design services with CRO-tested copy, design and full conversion tracking, delivered fast within just 48 hours for every client.", 160,
  "Landing page design agency", "Landing page design services"),
 ("Real Estate Lead Generation", "/services/real-estate-lead-generation/",
  "Real estate lead generation services | DigiVeritaz India", 56,
  "DigiVeritaz is a Real estate marketing agency that generated 100k+ qualified leads across 50+ RERA-aware projects for developers across India with real results.", 160,
  "Real estate lead generation services", "Real estate marketing agency"),
 ("Research and Insights", "/services/research-and-insights/",
  "Top Market research services for Businesses | DigiVeritaz", 57,
  "DigiVeritaz delivers Business insights through 300+ studies covering 50k+ respondents across India, turning research into smarter growth decisions every time.", 158,
  "Market research services", "Business insights"),
 ("Strategy and Planning", "/services/strategy-and-planning/",
  "Digital marketing strategy in India | DigiVeritaz India", 55,
  "DigiVeritaz offers Marketing strategy consulting with 200+ operator-led roadmaps built around your business goals, budget and stage, not a template every time.", 159,
  "Digital marketing strategy", "Marketing strategy consulting"),
 ("Analytics Configuration", "/services/analytics-configuration/",
  "Google Analytics setup services in India | DigiVeritaz India", 60,
  "DigiVeritaz offers GA4 configuration services covering 500+ setups, server-side tagging and Looker Studio dashboards built for accurate reporting every time.", 157,
  "Google Analytics setup services", "GA4 configuration services"),
 ("Google Tag Manager", "/services/google-tag-manager/",
  "Google Tag Manager services in India | DigiVeritaz India", 56,
  "DigiVeritaz offers GTM setup services that built 400+ containers with server-side GTM and Consent Mode v2 for clean, compliant tracking always built to perform.", 160,
  "Google Tag Manager services", "GTM setup services"),
 ("Data Strategy Consulting", "/services/data-strategy-consulting-services/",
  "Data strategy consulting services in India | DigiVeritaz", 56,
  "DigiVeritaz offers Marketing data consulting spanning 100+ programmes across BigQuery, Looker Studio and first-party data activation for brands every time.", 155,
  "Data strategy consulting services", "Marketing data consulting"),
 ("Website Development", "/services/website-development/",
  "Website development company in India | DigiVeritaz India", 56,
  "DigiVeritaz is a Web development agency that launched 500+ sites averaging 95+ Lighthouse scores, fast load times and Core Web Vitals-first builds every time.", 158,
  "Website development company", "Web development agency"),
 ("Custom Software Development", "/services/custom-software-development/",
  "Custom software development company | DigiVeritaz India", 55,
  "DigiVeritaz offers Software development services that shipped 100+ products, including 25+ SaaS platforms, built full-stack for growing companies every time.", 157,
  "Custom software development company", "Software development services"),
 ("Ecommerce Development", "/services/ecommerce-development/",
  "Ecommerce development company in India | DigiVeritaz India", 58,
  "DigiVeritaz offers Ecommerce website development services that launched 200+ stores driving Rs 500Cr+ in GMV as a certified Shopify Partner with real results.", 158,
  "Ecommerce development company", "Ecommerce website development services"),
 ("Wordpress Development", "/services/wordpress-development/",
  "WordPress development company in India | DigiVeritaz India", 58,
  "DigiVeritaz offers WordPress development services that shipped 300+ sites averaging 92+ Lighthouse scores, with custom themes and WooCommerce builds today.", 155,
  "WordPress development company", "WordPress development services"),
 ("Mobile App Development", "/services/mobile-app-development/",
  "Mobile app development company in India | DigiVeritaz India", 59,
  "DigiVeritaz offers Mobile app development services that built 75+ apps with 10M+ combined downloads across iOS, Android and React Native platforms every time.", 158,
  "Mobile app development company", "Mobile app development services"),
 ("Linux Hosting", "/services/linux-hosting/",
  "Linux hosting services for Businesses | DigiVeritaz India", 57,
  "DigiVeritaz offers Managed Linux hosting running 500+ servers at 99.99% uptime with round-the-clock, security-hardened NOC support for every client every time.", 159,
  "Linux hosting services", "Managed Linux hosting"),
 ("Business Email", "/services/business-email/",
  "Business email hosting for Businesses | DigiVeritaz India", 57,
  "DigiVeritaz offers Professional business email services covering 1,000+ mailboxes on Google Workspace and Microsoft 365 with zero-downtime migration today.", 155,
  "Business email hosting", "Professional business email services"),
 ("CRM", "/services/crm-services/",
  "CRM consulting services for Brands | DigiVeritaz Mumbai", 55,
  "DigiVeritaz offers CRM implementation services spanning 80+ deployments across HubSpot, Salesforce, Zoho and Pipedrive with built-in lead scoring every time.", 157,
  "CRM consulting services", "CRM implementation services"),
 ("Case Study", "/case-study/",
  "Digital marketing case studies in India | DigiVeritaz India", 59,
  "Browse DigiVeritaz's SEO case studies and real campaign results covering lead generation, SEO and PPC wins for brands across every industry in India today.", 155,
  "Digital marketing case studies", "SEO case studies"),
 ("Ai News", "/ai-news/",
  "Best AI marketing news for Businesses | DigiVeritaz India", 57,
  "Get DigiVeritaz's daily digest of AI tools for marketing and the latest AI news, delivered free to your inbox every single morning at 10am sharp every time.", 156,
  "AI marketing news", "AI tools for marketing"),
 ("Contact Us", "/contact-us/",
  "Hire digital marketing agency in India | DigiVeritaz India", 58,
  "Book a free Digital marketing consultation with DigiVeritaz to discuss SEO, PPC and performance marketing solutions for your business today with real results.", 158,
  "Hire digital marketing agency", "Digital marketing consultation"),
 ("Organic Marketing", "/services/organic-marketing/",
  "Organic marketing agency in Mumbai | DigiVeritaz Mumbai", 55,
  "DigiVeritaz offers Organic marketing services that shipped 1,000+ pieces of content across pillar pages and topic clusters that rank and convert every time.", 156,
  "Organic marketing agency", "Organic marketing services"),
 ("About Us", "/about-us/",
  "Digital marketing company in India | DigiVeritaz Mumbai", 55,
  "DigiVeritaz is a Digital transformation agency helping Indian brands grow through SEO, paid ads, branding and ROI-focused strategy since day one every time.", 156,
  "Digital marketing company", "Digital transformation agency"),
]

# Stock endings the sheet uses to pad each description to ~158 characters.
FILLERS = (" every time.", " with real results.", " built to perform.",
           " always built to perform.", " today.", " every single time.")


def strip_filler(desc):
    for f in FILLERS:
        if desc.endswith(f):
            return desc[: -len(f)].rstrip(" ,—-") + ".", f.strip()
    return desc, None


def main():
    inv_path = os.path.join(HERE, "data", "inventory.json")
    known = set()
    if os.path.isfile(inv_path):
        known = {p["path"] for p in json.load(open(inv_path, encoding="utf-8"))["pages"]}

    entries, bad_len, bad_path = [], [], []
    for name, path, title, t_len, desc, d_len, kw1, kw2 in ROWS:
        if known and path not in known:
            bad_path.append((name, path))
        if len(title) != t_len:
            bad_len.append((name, "title", t_len, len(title), title))
        if len(desc) != d_len:
            bad_len.append((name, "description", d_len, len(desc), desc))
        trimmed, filler = strip_filler(desc)
        entries.append({
            "page": name, "path": path,
            "title": title, "title_len": len(title),
            "description": desc, "description_len": len(desc),
            "description_trimmed": trimmed, "description_trimmed_len": len(trimmed),
            "filler_removed": filler,
            "primary_keyword": kw1, "secondary_keyword": kw2,
        })

    out = os.path.join(HERE, "data", "meta_plan.json")
    json.dump({"source": "Title and Description - DigiVeritaz (PDF export)",
               "count": len(entries), "entries": entries},
              open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"{len(entries)} rows -> {out}\n")
    print(f"length checksum : {len(ROWS)*2 - len(bad_len)}/{len(ROWS)*2} cells match the sheet")
    for n, kind, stated, got, val in bad_len:
        print(f"   MISMATCH {n} {kind}: sheet says {stated}, transcription is {got}")
        print(f"            {val!r}")
    print(f"\nURL check       : {len(ROWS) - len(bad_path)}/{len(ROWS)} paths exist in the sitemap")
    for n, p in bad_path:
        print(f"   NOT FOUND {n}: {p}")
    n_filler = sum(1 for e in entries if e["filler_removed"])
    print(f"\nfiller endings  : {n_filler}/{len(entries)} descriptions end in a stock phrase")
    if n_filler:
        avg = sum(e["description_len"] for e in entries) / len(entries)
        avgt = sum(e["description_trimmed_len"] for e in entries) / len(entries)
        print(f"                  mean length {avg:.0f} chars -> {avgt:.0f} if trimmed")
    return 1 if (bad_len or bad_path) else 0


if __name__ == "__main__":
    sys.exit(main())
