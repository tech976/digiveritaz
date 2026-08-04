#!/usr/bin/env python3
"""Build site/careers.html from the faq.html shell.

faq.html is the simplest hand-written page on the site, so its head, nav,
footer and script tail are reused verbatim -- that keeps the new page in
sync with everything else (GTM, schema graph, theme bootstrap, the Ask-AI
footer block) without hand-copying 200 lines that will drift.

Only the head metadata and the <main> body are replaced.

The open-roles section is deliberately built but empty: real vacancies
are a factual claim and have to come from the client. Once roles arrive,
fill ROLES below and re-run -- JobPosting schema is emitted automatically
so listings become eligible for the Google Jobs box.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
SRC = SITE / "faq.html"
OUT = SITE / "careers.html"

TITLE = "Careers at DigiVeritaz | Digital Marketing Jobs in Mumbai"
DESC = (
    "Build your career at DigiVeritaz, a Mumbai-based digital marketing agency. "
    "See our open positions and apply online."
)
KEYWORDS = (
    "digital marketing jobs Mumbai, careers DigiVeritaz, SEO jobs Mumbai, "
    "PPC jobs India, performance marketing careers, content writer jobs Mumbai, "
    "web developer jobs Chembur, digital marketing agency careers India"
)
URL = "https://www.digiveritaz.com/careers/"
APPLY = "info@digiveritaz.com"

# ---------------------------------------------------------------------------
# Real vacancies go here. Each entry:
#   title, team, location, type, experience, about, responsibilities[], skills[]
# Leave empty for the "no open roles right now" state.
# ---------------------------------------------------------------------------
# Each role: title, team, location, type, experience, about, then any number of
# sections. A section is {"h": heading, "items": [...]} with optional "intro"
# and "outro" paragraphs. months_experience is optional and only feeds schema.
ROLES = [
    {
        "title": "Frontend Developer Intern",
        "blurb": "Turn designs into pixel-accurate, responsive interfaces with React, Next.js and Tailwind &mdash; and improve the design where it falls short.",
        "team": "Engineering",
        "location": "Onsite &mdash; Chembur, Mumbai",
        "type": "Internship",
        "experience": "Open to all applicants",
        "schema_type": "INTERN",
        "about": (
            "We build performance-driven digital solutions powered by technology, creativity, data "
            "and AI &mdash; scalable web platforms, marketing technology, automation systems and "
            "AI-integrated workflows. This internship is for people who write clean, modern frontend "
            "code and genuinely care how a product looks and feels: spacing, typography, colour, "
            "motion, polish. You should be able to take a design concept and turn it into a "
            "pixel-accurate, responsive, high-performance interface &mdash; and be just as "
            "comfortable improving that design where it falls short."
        ),
        "sections": [
            {"h": "Key responsibilities", "items": [
                "Develop responsive, accessible and visually refined interfaces for modern web applications",
                "Convert UI/UX designs, wireframes and prototypes into clean, production-ready code",
                "Maintain visual consistency using design systems, component libraries and defined colour and type standards",
                "Work with designers, backend developers, strategists and marketing to deliver cohesive experiences",
                "Build and integrate REST APIs and third-party services into frontend applications",
                "Optimise for performance, cross-browser compatibility and mobile responsiveness",
                "Take part in testing, debugging, deployment and continuous UI improvement",
                "Use AI-powered development and design tools to accelerate build cycles and improve code quality",
            ]},
            {"h": "Required skills", "items": [
                "Background in CS, IT, Design, AI or a related field &mdash; or equivalent practical experience shown through projects and portfolio work",
                "Strong command of HTML, CSS and JavaScript, plus modern web development concepts",
                "Working knowledge of React.js or Next.js",
                "Good understanding of responsive design, Flexbox/Grid and modern CSS approaches such as Tailwind",
                "A strong sense of visual design &mdash; layout, hierarchy, spacing, typography, colour",
                "Understanding of UI/UX principles and the ability to translate design intent accurately into code",
                "Familiarity with Git/GitHub",
                "Strong analytical thinking, problem-solving and attention to detail",
                "Good communication and the ability to work in a collaborative team",
            ]},
            {"h": "Mandatory &mdash; AI tool proficiency",
             "intro": "You must be comfortable with modern AI-assisted development, design and productivity tools, such as:",
             "items": [
                 "ChatGPT, Claude",
                 "GitHub Copilot, Cursor",
                 "Figma and AI-assisted design-to-code tools",
                 "Midjourney / Runway or similar AI creative tools",
             ],
             "outro": "You should understand how AI improves development efficiency, accelerates design-to-development workflows and supports modern engineering practice."},
            {"h": "Preferred", "items": [
                "Component libraries and design systems such as shadcn/ui, Material UI or Chakra UI",
                "Animation and interaction libraries such as Framer Motion or GSAP",
                "Basic understanding of backend technologies, APIs and databases",
                "Deployment platforms such as Vercel, Netlify or AWS",
                "Awareness of web accessibility standards, SEO fundamentals and Core Web Vitals",
                "A portfolio of personal projects, freelance work, hackathons, internships or open-source contributions",
            ]},
            {"h": "What we offer", "items": [
                "Real-world, high-impact projects",
                "Exposure to modern development practice and AI-integrated workflows",
                "Hands-on learning under experienced professionals",
                "Potential full-time role based on performance",
            ]},
            {"h": "Eligibility", "items": [
                "Open to all &mdash; students, freshers and self-taught developers with a strong portfolio are equally welcome",
            ]},
        ],
    },
    {
        "title": "UI/UX Developer Intern",
        "blurb": "Research, wireframe and design product experiences, then take them forward into clean, working frontend code.",
        "team": "Design &amp; Engineering",
        "location": "Onsite &mdash; Chembur, Mumbai",
        "type": "Internship",
        "experience": "Open to all applicants",
        "schema_type": "INTERN",
        "about": (
            "We build performance-driven digital solutions powered by technology, creativity, data "
            "and AI &mdash; scalable web platforms, marketing technology, automation systems and "
            "AI-integrated workflows. This is a hybrid role for people who think like designers and "
            "build like developers: someone who can research, wireframe and design a product "
            "experience, then take it forward into working, well-structured code. You should have a "
            "genuine understanding of what makes a design good &mdash; colour, contrast, typography, "
            "spacing, hierarchy, usability &mdash; and be confident using AI tools to iterate at "
            "speed while still applying your own judgement to everything you ship."
        ),
        "sections": [
            {"h": "Key responsibilities", "items": [
                "Design intuitive, modern user interfaces for websites, web apps and digital campaigns",
                "Create wireframes, user flows, prototypes and high-fidelity mockups in Figma",
                "Apply colour theory, typography, spacing and visual hierarchy across all deliverables",
                "Build and maintain design systems, UI component libraries and brand style guides",
                "Translate approved designs into clean, responsive frontend code with the dev team",
                "Run basic user research, usability reviews and design iterations from feedback and performance data",
                "Work with developers, strategists and marketers so design serves both UX and business goals",
                "Use AI-powered design and development tools to generate concepts and accelerate iteration",
            ]},
            {"h": "Required skills", "items": [
                "Background in Design, CS, IT, HCI, AI or a related field &mdash; or equivalent practical experience shown through a strong portfolio",
                "Demonstrated understanding of colour theory, typography, layout, spacing, contrast and visual hierarchy",
                "Solid grasp of UI/UX fundamentals: user flows, information architecture, usability and accessibility",
                "Proficiency in Figma (Adobe XD, Sketch or similar also fine)",
                "Working knowledge of HTML, CSS and JavaScript, with the ability to implement designs in code",
                "Basic understanding of React.js or Next.js",
                "Able to explain and justify design decisions, not just rely on aesthetics",
                "Familiarity with Git/GitHub",
                "Good communication and the ability to work in a collaborative team",
                "<strong>A portfolio or design samples are required for this role</strong>",
            ]},
            {"h": "Mandatory &mdash; AI tool proficiency",
             "intro": "You must be comfortable with modern AI-assisted design, development and productivity tools, such as:",
             "items": [
                 "ChatGPT, Claude",
                 "Midjourney, Runway",
                 "Figma AI features and AI-assisted design tools",
                 "Cursor / GitHub Copilot",
                 "Adobe Firefly, Canva AI or similar AI creative platforms",
             ],
             "outro": "You should understand how AI accelerates design exploration, refines visual concepts and improves development efficiency &mdash; while still applying independent judgement to the final output."},
            {"h": "Preferred", "items": [
                "Experience with design systems and component libraries",
                "Familiarity with Tailwind CSS, shadcn/ui or similar",
                "Motion design and micro-interactions &mdash; Framer Motion, After Effects or Lottie",
                "Responsive design across devices and web accessibility standards",
                "Landing page, conversion-focused or marketing creative work",
                "Deployment platforms such as Vercel or Netlify",
                "Personal projects, freelance work, hackathons, internships or open-source contributions",
            ]},
            {"h": "What we offer", "items": [
                "Real-world, high-impact projects",
                "Exposure to modern design practice and AI-integrated creative workflows",
                "Hands-on learning under experienced professionals",
                "Creative ownership over how our products look and feel",
                "Potential full-time role based on performance",
            ]},
            {"h": "Eligibility", "items": [
                "Open to all &mdash; students, freshers, self-taught designers and career-switchers with a strong portfolio are equally welcome",
            ]},
        ],
    },
    {
        "title": "Business Development Associate",
        "blurb": "Find opportunities, run outreach across email and LinkedIn, and build the pipeline behind our growth.",
        "team": "Business Development",
        "location": "Onsite &mdash; Chembur, Mumbai",
        "type": "Full-time",
        "experience": "1&ndash;3 years",
        "schema_type": "FULL_TIME",
        "months_experience": 12,
        "about": (
            "We&rsquo;re a performance-driven AI marketing company working across e-commerce, "
            "applications, finance, real estate, SaaS, B2B and B2C. With a growing focus on AI "
            "automation and smart marketing systems, we help brands achieve scalable, measurable "
            "growth. We&rsquo;re looking for someone enthusiastic and proactive, eager to learn "
            "the business side of marketing."
        ),
        "sections": [
            {"h": "Key responsibilities", "items": [
                "Research and identify potential clients and market opportunities",
                "Generate leads via email campaigns, LinkedIn outreach and other channels",
                "Prepare pitch decks, proposals and other business development materials",
                "Handle follow-ups and coordination",
                "Maintain and update CRM tools such as HubSpot and Zoho CRM",
            ]},
            {"h": "Requirements", "items": [
                "Strong verbal and written communication",
                "Working knowledge of Excel, Google Sheets and CRM tools",
                "Interest in digital marketing, AI and business strategy",
                "Able to work independently and take initiative",
                "A learning mindset, with attention to detail",
            ]},
        ],
    },
]



def subject_for(r):
    from urllib.parse import quote
    # plain hyphen, matching the subject line the listings ask applicants to use
    return quote(f"Application - {r['title']}", safe="")


def role_card(r):
    import html as _h
    plain_title = _h.unescape(r['title'])

    def block(sec):
        out = f'          <h4 class="job-sub">{sec["h"]}</h4>\n'
        if sec.get("intro"):
            out += f'          <p class="job-note">{sec["intro"]}</p>\n'
        if sec.get("items"):
            lis = "\n".join(f"            <li>{i}</li>" for i in sec["items"])
            out += f'          <ul class="job-list">\n{lis}\n          </ul>\n'
        if sec.get("outro"):
            out += f'          <p class="job-note">{sec["outro"]}</p>\n'
        return out

    body_sections = "".join(block(s) for s in r.get("sections", []))
    apply_note = (
        f'          <p class="job-note">{r["apply_note"]}</p>\n' if r.get("apply_note") else ""
    )

    return f"""      <div class="job-card">
        <details class="job-det">
        <summary class="job-summary">
          <span class="job-sum-text">
            <span class="job-team">{r['team']}</span>
            <h3>{r['title']}</h3>
            <p class="job-blurb">{r['blurb']}</p>
            <span class="job-meta">
              <span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>{r['location']}</span>
              <span><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>{r['type']}</span>
              <span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>{r['experience']}</span>
            </span>
          </span>
          <span class="job-more">
            <span class="job-more-txt">View details</span>
            <span class="job-caret" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
            </span>
          </span>
        </summary>
        <div class="job-body">
          <p>{r['about']}</p>
{body_sections}{apply_note}          <a class="btn btn-primary" href="#apply" data-role="{plain_title}">Apply for this role</a>
        </div>
        </details>
        <a class="btn btn-primary job-apply" href="#apply" data-role="{plain_title}">Apply</a>
      </div>"""


def roles_section():
    if not ROLES:
        return """      <div class="job-empty">
        <p><strong>Nothing formally advertised right now.</strong></p>
        <p>We still keep good applications on file and get in touch when something opens up.</p>
        <a class="btn btn-primary" href="#apply">Send an open application</a>
      </div>"""
    return '<div class="job-grid">\n' + "\n".join(role_card(r) for r in ROLES) + "\n      </div>"


# Google requires datePosted on JobPosting. Set it when a role is added, and
# refresh it if a role is re-advertised -- a stale date pushes listings down.
DATE_POSTED = "2026-08-04"


def job_schema():
    if not ROLES:
        return ""
    import json
    import html as _html

    def plain(s):
        return _html.unescape(s)

    out = []
    for r in ROLES:
        desc = "<p>" + plain(r["about"]) + "</p>"
        for sec in r.get("sections", []):
            desc += f"<p><strong>{plain(sec['h'])}</strong></p>"
            if sec.get("intro"):
                desc += f"<p>{plain(sec['intro'])}</p>"
            if sec.get("items"):
                desc += "<ul>" + "".join(f"<li>{plain(i)}</li>" for i in sec["items"]) + "</ul>"
            if sec.get("outro"):
                desc += f"<p>{plain(sec['outro'])}</p>"

        exp = None
        if r.get("months_experience") is not None:
            exp = {"@type": "OccupationalExperienceRequirements",
                   "monthsOfExperience": r["months_experience"]}

        out.append(json.dumps({
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": plain(r["title"]),
            "description": desc,
            "datePosted": DATE_POSTED,
            "employmentType": r.get("schema_type") or r["type"].upper().replace("-", "_").replace(" ", "_"),
            "hiringOrganization": {"@id": "https://www.digiveritaz.com/#organization"},
            "jobLocation": {"@type": "Place", "address": {
                "@type": "PostalAddress",
                "streetAddress": "1st Floor, Ujagar Chambers, Bus Depot, Sion-Trombay Rd, opp. Deonar, Chembur",
                "addressLocality": "Mumbai", "addressRegion": "Maharashtra",
                "postalCode": "400088", "addressCountry": "IN"}},
            "jobLocationType": None if "Onsite" in plain(r["location"]) else "TELECOMMUTE",
            "experienceRequirements": exp,
            "directApply": True,
            "url": URL + "#open-roles",
        }, separators=(",", ":")))
    # drop null keys rather than emit them
    out = [json.dumps({k: v for k, v in json.loads(o).items() if v is not None},
                      separators=(",", ":")) for o in out]
    return "\n".join(f'<script type="application/ld+json">{o}</script>' for o in out)


# The Apply link deliberately sits OUTSIDE <summary>, laid next to it with CSS
# grid. Inside, a click on it also fires the summary's activation behaviour and
# toggles the card -- and stopPropagation does not prevent that, because the
# activation target is fixed when the event path is computed. Keeping it a
# sibling makes the whole thing work with no JavaScript at all.
APPLY_SCRIPT = ""

# ---------------------------------------------------------------------------
# Recruitment form -> its OWN Google Sheet, separate from the lead form.
#
# CAREERS_ENDPOINT must be the /exec URL of the Apps Script Web App deployed
# from _ops/apps-script-careers-form.gs and bound to the careers spreadsheet.
# It is intentionally blank: pointing it at the lead-form endpoint would push
# applicants into the sales pipeline. While blank, the form renders but refuses
# to submit and says so, rather than silently dropping applications.
# ---------------------------------------------------------------------------
CAREERS_ENDPOINT = "https://script.google.com/macros/s/AKfycbwUcz_-vC_B4zLk3WqMGgqmSrlE1LW8Y76VomJlozrQsRXjCKsZNprTiaufHMr2ZZdy/exec"

EXPERIENCE_OPTS = ["Student", "Fresher (0-1 year)", "1-3 years", "3-5 years", "5+ years"]
AVAILABILITY_OPTS = ["Immediately", "Within 15 days", "Within 30 days", "More than 30 days"]
SOURCE_OPTS = ["LinkedIn", "Instagram", "Google search", "Referral", "Naukri / job board", "Other"]


def _opts(values, placeholder):
    out = [f'<option value="" disabled selected>{placeholder}</option>']
    out += [f'<option value="{v}">{v}</option>' for v in values]
    return "\n            ".join(out)


def _role_opts():
    import html as _h
    vals = [_h.unescape(r["title"]) for r in ROLES] + ["Open application (no specific role)"]
    return _opts(vals, "Select a role")


FORM = f"""    <form id="careers-form" novalidate>
      <div class="cf-grid">
        <div class="cf-field">
          <label for="ca-name">Full name <span class="req">*</span></label>
          <input type="text" id="ca-name" name="fullname" required autocomplete="name" placeholder="Your full name">
        </div>
        <div class="cf-field">
          <label for="ca-email">Email <span class="req">*</span></label>
          <input type="email" id="ca-email" name="email" required autocomplete="email" placeholder="you@example.com">
        </div>
        <div class="cf-field">
          <label for="ca-phone">Phone <span class="req">*</span></label>
          <span class="otp-row">
            <input type="tel" id="ca-phone" name="phone" required autocomplete="tel" placeholder="10-digit mobile number">
            <button type="button" class="otp-btn" id="ca-getotp">Send OTP</button>
          </span>
          <span class="otp-row" id="ca-otp-row" hidden>
            <input type="text" id="ca-otp" name="otp" inputmode="numeric" maxlength="6" placeholder="6-digit code" autocomplete="one-time-code">
            <button type="button" class="otp-btn" id="ca-verify">Verify</button>
          </span>
          <span class="otp-msg" id="ca-otp-msg" role="status" aria-live="polite"></span>
        </div>
        <div class="cf-field">
          <label for="ca-role">Role you&rsquo;re applying for <span class="req">*</span></label>
          <select id="ca-role" name="role" required>
            {_role_opts()}
          </select>
        </div>
        <div class="cf-field">
          <label for="ca-city">Current city <span class="req">*</span></label>
          <input type="text" id="ca-city" name="city" required placeholder="e.g. Mumbai">
        </div>
        <div class="cf-field">
          <label for="ca-exp">Experience level <span class="req">*</span></label>
          <select id="ca-exp" name="experience" required>
            {_opts(EXPERIENCE_OPTS, "Select experience")}
          </select>
        </div>
        <div class="cf-field">
          <label for="ca-edu">Qualification / background</label>
          <input type="text" id="ca-edu" name="education" placeholder="e.g. B.Des, BSc CS, self-taught">
        </div>
        <div class="cf-field">
          <label for="ca-avail">Availability to start <span class="req">*</span></label>
          <select id="ca-avail" name="availability" required>
            {_opts(AVAILABILITY_OPTS, "Select availability")}
          </select>
        </div>
        <div class="cf-field cf-full">
          <label for="ca-resume">Resume link <span class="req">*</span></label>
          <input type="url" id="ca-resume" name="resume_link" required placeholder="Google Drive / Dropbox link (make sure it&rsquo;s publicly viewable)">
        </div>
        <div class="cf-field cf-full">
          <label for="ca-portfolio">Portfolio / GitHub / live project links</label>
          <input type="url" id="ca-portfolio" name="portfolio_link" placeholder="Figma, Behance, Dribbble, GitHub or a live URL">
        </div>
        <div class="cf-field">
          <label for="ca-linkedin">LinkedIn</label>
          <input type="url" id="ca-linkedin" name="linkedin" placeholder="linkedin.com/in/&hellip;">
        </div>
        <div class="cf-field">
          <label for="ca-stipend">Expected stipend / salary</label>
          <input type="text" id="ca-stipend" name="expected_pay" placeholder="Per month, or &lsquo;negotiable&rsquo;">
        </div>
        <div class="cf-field cf-full">
          <label for="ca-ai">AI tools you use</label>
          <input type="text" id="ca-ai" name="ai_tools" placeholder="e.g. ChatGPT, Claude, Cursor, Figma AI, Copilot">
        </div>
        <div class="cf-field">
          <label for="ca-source">How did you hear about us?</label>
          <select id="ca-source" name="source">
            {_opts(SOURCE_OPTS, "Select one")}
          </select>
        </div>
        <div class="cf-field cf-full">
          <label for="ca-note">Anything else we should know?</label>
          <textarea id="ca-note" name="note" rows="4" maxlength="1200" placeholder="A short note on what you want to work on, or a project you&rsquo;re proud of."></textarea>
        </div>
      </div>

      <label class="cf-consent">
        <input type="checkbox" name="consent" value="yes" required>
        <span>I agree that DigiVeritaz may store and process the details above to consider me for this and future roles. <span class="req">*</span></span>
      </label>

      <input type="text" name="_hp_site" tabindex="-1" autocomplete="off" aria-hidden="true" class="cf-hp">
      <input type="text" name="_hp_addr" tabindex="-1" autocomplete="off" aria-hidden="true" class="cf-hp">
      <input type="hidden" id="ca-ts" name="_ts">
      <input type="hidden" id="ca-jsok" name="_jsok">

      <div class="cf-actions">
        <button type="submit" class="btn btn-primary" id="ca-submit" disabled>Submit application</button>
        <p class="cf-msg" id="ca-msg" role="status" aria-live="polite"></p>
      </div>
    </form>

    <script>
    (function(){{
      // Stamp synchronously -- the hidden inputs are above this script, so they
      // exist now. Doing it on DOMContentLoaded left them blank on the contact
      // form and Apps Script rejected those submissions.
      try {{
        document.getElementById('ca-ts').value = String(Date.now());
        document.getElementById('ca-jsok').value = 'dv-' + Math.random().toString(36).slice(2, 12);
      }} catch(e) {{}}

      var ENDPOINT = '{CAREERS_ENDPOINT}';
      var MSG91 = {{ widgetId: '3666766e6633313737383230', tokenAuth: '520932TU9OQwuB86a3942beP1' }};

      var panel = document.getElementById('apply');
      var form  = document.getElementById('careers-form');
      var msg   = document.getElementById('ca-msg');
      var btn   = document.getElementById('ca-submit');
      var sel   = document.getElementById('ca-role');
      var label = document.getElementById('ca-role-label');
      var closeBtn = document.getElementById('ca-close');

      var phoneEl = document.getElementById('ca-phone');
      var getBtn  = document.getElementById('ca-getotp');
      var otpRow  = document.getElementById('ca-otp-row');
      var otpEl   = document.getElementById('ca-otp');
      var verBtn  = document.getElementById('ca-verify');
      var otpMsg  = document.getElementById('ca-otp-msg');

      var ready = false, verified = false, sent = false;

      function say(t, ok){{ msg.textContent = t || ''; msg.className = 'cf-msg' + (ok === true ? ' is-ok' : ok === false ? ' is-err' : ''); }}
      function omsg(t, kind){{ otpMsg.textContent = t || ''; otpMsg.className = 'otp-msg' + (kind ? ' is-' + kind : ''); }}
      function digits(){{ return (phoneEl.value || '').replace(/[^0-9]/g, '').slice(-10); }}
      function phoneOk(){{ return /^[6-9][0-9]{{9}}$/.test(digits()); }}
      function setSubmit(){{ btn.disabled = !verified; btn.style.opacity = verified ? '1' : '.55'; }}
      setSubmit();

      // ---- open / close -------------------------------------------------
      function openPanel(role){{
        panel.classList.add('is-open');
        if (role) {{
          for (var i = 0; i < sel.options.length; i++) {{
            if (sel.options[i].value === role) {{ sel.selectedIndex = i; break; }}
          }}
        }}
        label.textContent = sel.value || 'a role';
        try {{ panel.scrollIntoView({{behavior: 'smooth', block: 'start'}}); }} catch(e) {{ panel.scrollIntoView(); }}
        setTimeout(function(){{ try {{ document.getElementById('ca-name').focus({{preventScroll: true}}); }} catch(e) {{}} }}, 420);
      }}
      document.querySelectorAll('[data-role], .job-apply').forEach(function(a){{
        a.addEventListener('click', function(e){{ e.preventDefault(); openPanel(a.getAttribute('data-role')); }});
      }});
      sel.addEventListener('change', function(){{ label.textContent = sel.value || 'a role'; }});
      closeBtn.addEventListener('click', function(){{
        panel.classList.remove('is-open');
        try {{ document.getElementById('open-roles').scrollIntoView({{behavior: 'smooth', block: 'start'}}); }} catch(e) {{}}
      }});
      if (location.hash === '#apply') openPanel(null);

      // ---- OTP (same MSG91 widget as the contact form) -------------------
      function initMsg91(){{
        if (ready) return true;
        if (typeof window.initSendOTP !== 'function') return false;
        try {{
          window.initSendOTP({{widgetId: MSG91.widgetId, tokenAuth: MSG91.tokenAuth, exposeMethods: true,
                              success: function(){{}}, failure: function(){{}}}});
          ready = true;
        }} catch(e) {{}}
        return ready;
      }}
      function loadMsg91(cb){{
        if (initMsg91()) {{ cb(true); return; }}
        var urls = ['https://verify.msg91.com/otp-provider.js', 'https://verify.phone91.com/otp-provider.js'], i = 0;
        (function go(){{
          var sc = document.createElement('script');
          sc.src = urls[i]; sc.async = true;
          sc.onload = function(){{ cb(initMsg91()); }};
          sc.onerror = function(){{ i++; if (i < urls.length) go(); else cb(false); }};
          document.head.appendChild(sc);
        }})();
      }}

      phoneEl.addEventListener('input', function(){{ if (verified) {{ verified = false; setSubmit(); }} }});
      otpEl.addEventListener('input', function(){{ otpEl.value = otpEl.value.replace(/[^0-9]/g, '').slice(0, 6); }});

      getBtn.addEventListener('click', function(){{
        if (!phoneOk()) {{ omsg('Enter a valid 10-digit mobile number.', 'err'); return; }}
        var isResend = sent;
        getBtn.disabled = true;
        omsg(isResend ? 'Sending a new code…' : 'Sending OTP…');
        loadMsg91(function(ok){{
          if (!ok || typeof window.sendOtp !== 'function') {{
            getBtn.disabled = false; omsg('Could not reach the OTP service. Please try again.', 'err'); return;
          }}
          var onSent = function(){{
            sent = true; getBtn.disabled = false; getBtn.textContent = 'Resend';
            otpRow.hidden = false;
            omsg('OTP sent to +91 ' + digits() + ' via SMS.', 'ok');
            try {{ otpEl.focus(); }} catch(e) {{}}
          }};
          var onErr = function(err){{
            getBtn.disabled = false;
            try {{ console.error('MSG91 sendOtp', err); }} catch(e) {{}}
            omsg('Could not send OTP — check the number and try again.', 'err');
          }};
          if (isResend && window.retryOtp) window.retryOtp(null, onSent, onErr);
          else window.sendOtp('91' + digits(), onSent, onErr);
        }});
      }});

      verBtn.addEventListener('click', function(){{
        var code = (otpEl.value || '').trim();
        if (code.length < 4) {{ omsg('Enter the code we sent you.', 'err'); return; }}
        if (typeof window.verifyOtp !== 'function') {{ omsg('Verification not ready — please resend the code.', 'err'); return; }}
        verBtn.disabled = true; omsg('Verifying…');
        window.verifyOtp(code, function(){{
          verified = true; verBtn.disabled = false;
          otpRow.hidden = true;
          getBtn.textContent = 'Verified ✓'; getBtn.disabled = true; getBtn.style.background = '#16a34a';
          phoneEl.readOnly = true;
          omsg('Mobile number verified ✓', 'ok');
          setSubmit(); say('');
        }}, function(err){{
          verBtn.disabled = false;
          try {{ console.error('MSG91 verifyOtp', err); }} catch(e) {{}}
          omsg('Incorrect or expired code. Resend and try again.', 'err');
        }});
      }});

      // ---- submit --------------------------------------------------------
      form.addEventListener('submit', function(e){{
        e.preventDefault();
        if (!verified) {{ say('Please verify your mobile number first.', false); return; }}
        if (!form.checkValidity()) {{ form.reportValidity(); return; }}
        if (!ENDPOINT) {{ say('Applications aren’t open through this form yet. Please check back shortly.', false); return; }}

        var fd = new FormData(form), body = new URLSearchParams();
        fd.forEach(function(v, k){{ body.append(k, v); }});
        body.append('action', 'application_save');
        body.append('applicationId', 'ca-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8));
        body.append('otp_verified', 'yes');
        body.append('_source', 'website-careers-form');
        body.append('_page', location.pathname || '/careers/');
        body.append('_subject', 'New job application — DigiVeritaz careers');
        // carry the site-wide UTM attribution, same as the contact form
        try {{
          var at = (typeof window.dvAttr === 'function') ? window.dvAttr() : {{}};
          for (var k in at) {{ if (at[k]) body.set(k, at[k]); }}
        }} catch(err) {{}}

        btn.disabled = true; btn.style.opacity = '.6';
        say('Sending…');

        var okBeacon = false;
        try {{
          okBeacon = !!(navigator.sendBeacon && navigator.sendBeacon(ENDPOINT,
            new Blob([body.toString()], {{type: 'application/x-www-form-urlencoded;charset=UTF-8'}})));
        }} catch(err) {{}}
        if (!okBeacon) {{
          fetch(ENDPOINT, {{method: 'POST', body: body, mode: 'no-cors', keepalive: true}}).catch(function(){{}});
        }}
        // no-cors gives no readable response, so confirm optimistically -- same
        // as the contact form.
        setTimeout(function(){{
          form.reset(); verified = false; sent = false;
          getBtn.textContent = 'Send OTP'; getBtn.disabled = false; getBtn.style.background = '';
          phoneEl.readOnly = false; otpRow.hidden = true; omsg('');
          say('Thanks — your application is in. We read every one and will be in touch if there’s a fit.', true);
          setSubmit();
        }}, 600);
      }});
    }})();
    </script>"""

BODY = f"""<main id="main" role="main">
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb">Home / Careers</div>
    <h1 class="play">Careers at <span class="green_text">DigiVeritaz</span></h1>
    <p class="lead">A Mumbai-based digital marketing agency. We hire people who want to own outcomes, not tick off tasks.</p>
  </div>
</section>

<section class="c-about">
  <div class="container prose" style="max-width:1120px">
    <h2 id="open-roles" style="scroll-margin-top:90px">Open positions</h2>
{roles_section()}
  </div>
</section>

<section class="c-apply" id="apply" style="scroll-margin-top:80px">
  <div class="container" style="max-width:820px">
    <div class="apply-head">
      <div>
        <h2>Apply</h2>
        <p class="apply-lead">Applying for <strong id="ca-role-label">a role</strong>. Fields marked <span class="req">*</span> are required.</p>
      </div>
      <button type="button" class="apply-close" id="ca-close" aria-label="Close application form">&times;</button>
    </div>
{FORM}
  </div>
</section>

</main>"""


def main():
    src = SRC.read_text(encoding="utf-8")

    head_end = src.index("<main id=\"main\" role=\"main\">")
    tail_start = src.index("</main>") + len("</main>")
    head, tail = src[:head_end], src[tail_start:]

    # --- rewrite head metadata -------------------------------------------
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*"', r"\g<1>" + DESC + '"', head)
    head = re.sub(r'(<meta name="keywords" content=")[^"]*"', r"\g<1>" + KEYWORDS + '"', head)
    head = head.replace("https://www.digiveritaz.com/faq/", URL)
    for prop in ("og:title", "twitter:title"):
        head = re.sub(rf'((?:property|name)="{prop}" content=")[^"]*"', r"\g<1>" + TITLE + '"', head)
    for prop in ("og:description", "twitter:description"):
        head = re.sub(rf'((?:property|name)="{prop}" content=")[^"]*"', r"\g<1>" + DESC + '"', head)
    head = re.sub(r'(<meta property="og:image:alt" content=")[^"]*"',
                  r"\g<1>Careers at DigiVeritaz — digital marketing jobs in Mumbai\"", head)

    # breadcrumb: FAQ -> Careers
    head = head.replace('"name":"FAQ"', '"name":"Careers"')
    head = re.sub(r'("@type":"ListItem","position":3,"name":")[^"]*"', r"\g<1>Careers\"", head)

    # faq.html carries FAQPage schema listing its own questions -- emitting
    # that here would be invalid structured data for a careers page.
    head, n = re.subn(
        r'<script type="application/ld\+json">\{"@context":"https://schema\.org","@type":"FAQPage".*?</script>\n?',
        "", head, flags=re.S)
    print(f"  stripped FAQPage schema blocks: {n}")

    js = job_schema()
    if js:
        head = head.replace("</head>", js + "\n</head>")

    OUT.write_text(head + BODY + tail, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(OUT.read_text(encoding='utf-8')):,} bytes)")
    print(f"  open roles listed: {len(ROLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
