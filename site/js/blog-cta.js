/* DV-BLOG-CTA v1 — requirement-gathering sidebar form + mid-article CTA for blog posts.

   Loaded automatically by main.js on any /blog/<slug>/ page, so EVERY existing post and
   every future post picks this up with no per-file HTML editing. Nothing to remember when
   publishing a new blog.

   It:
     1. re-flows the single-column article into [ sidebar | article ] on desktop,
     2. injects the "Let's Get Started" lead form into the left sidebar (sticky),
     3. injects a CTA band roughly half-way through the article body,
     4. on submit: saves the lead via sendBeacon (survives navigation, same transport the
        rest of the site uses so the Apps Script write + automated email still fire), pushes
        the conversion to dataLayer, then lands on /thank-you/?src=blog&lid=<id>.
*/
;(function () {
  if (window.__dvBlogCta) return; window.__dvBlogCta = true;

  var ENDPOINT = 'https://script.google.com/macros/s/AKfycby3DZjNUqSEU2Pg2rv45pnYTZT78L4405Et0SJ_NOBybsDLyd6ZWzxlSaEMx1TnKZkc/exec';

  /* same 12 services as the popup / contact form so Sheet columns stay identical */
  var SERVICES = ['Organic Marketing','Paid Social Media Advertising','Pay-Per-Click Advertising',
    'Performance Marketing','E-commerce Platforms','Data Strategy & Consulting','Native Advertising',
    'WhatsApp Marketing','Branding & Design','Search Engine Optimization',
    'Generative Search Optimisation','Tech & Development'];

  var LEAD_ID = 'blog-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8);

  function esc(s){ return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

  /* ---------------- styles ---------------- */
  function css() {
    if (document.getElementById('dvb-css')) return;
    var s = document.createElement('style');
    s.id = 'dvb-css';
    s.textContent = [
      /* widen the article container only when the sidebar is in play */
      '.blog-article.dvb-on .container{max-width:1200px}',
      '.dvb-grid{display:grid;grid-template-columns:340px minmax(0,1fr);gap:40px;align-items:start}',
      '.dvb-main{min-width:0}',
      /* --dvb-top is measured at runtime from the real sticky header (topbar + nav pill)
         so the card never tucks under it; the 150px fallback covers a no-JS/odd case. */
      '.dvb-side{position:sticky;top:var(--dvb-top,150px)}',

      /* form card */
      '.dvb-form{background:#fff;border:1px solid #e5e7eb;border-radius:18px;padding:22px 20px;box-shadow:0 18px 40px -28px rgba(2,6,23,.45)}',
      '.dvb-form h3{margin:0 0 4px;font-family:"Inter Tight",Inter,sans-serif;font-size:1.25rem;font-weight:800;color:#0b1220;letter-spacing:-.01em}',
      '.dvb-form .dvb-sub{margin:0 0 14px;font-size:.86rem;line-height:1.5;color:#64748b}',
      '.dvb-f{margin:0 0 10px}',
      '.dvb-f input,.dvb-f select,.dvb-f textarea{width:100%;box-sizing:border-box;padding:12px 13px;border:1.5px solid #e5e7eb;border-radius:11px;font-size:.95rem;font-family:inherit;color:#0f172a;background:#fff;outline:none;transition:border-color .2s,box-shadow .2s}',
      '.dvb-f textarea{resize:vertical;min-height:78px}',
      '.dvb-f input:focus,.dvb-f select:focus,.dvb-f textarea:focus{border-color:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.15)}',
      '.dvb-consent{display:flex;gap:8px;align-items:flex-start;margin:6px 0 12px;font-size:.74rem;color:#64748b;line-height:1.45}',
      '.dvb-consent input{flex:0 0 auto;width:16px;height:16px;margin-top:1px;accent-color:#16a34a;cursor:pointer}',
      '.dvb-consent a{color:#16a34a;text-decoration:none}',
      '.dvb-btn{width:100%;border:0;border-radius:12px;padding:13px 16px;font-family:inherit;font-weight:800;font-size:1rem;color:#06230f;background:linear-gradient(135deg,#22c55e,#16a34a);cursor:pointer;box-shadow:0 12px 26px -12px rgba(22,163,74,.55);transition:transform .15s,opacity .2s}',
      '.dvb-btn:hover{transform:translateY(-1px)}',
      '.dvb-btn[disabled]{background:#e2e8f0;color:#94a3b8;box-shadow:none;cursor:not-allowed;transform:none}',
      '.dvb-err{min-height:1em;margin-top:8px;font-size:.8rem;color:#dc2626;text-align:center}',
      '.dvb-trust{margin:12px 0 0;padding-top:12px;border-top:1px dashed #e5e7eb;font-size:.74rem;color:#64748b;text-align:center;line-height:1.5}',

      /* mid-article CTA.
         Selectors are scoped under `.blog-article .prose` because the site's own
         `.blog-article .prose h3 / a` rules are more specific than a bare `.dvb-mid h3`
         and would otherwise paint this dark-on-dark. */
      '.blog-article .prose .dvb-mid{margin:2.4em 0;border-radius:18px;padding:28px 24px;background:linear-gradient(135deg,#0b1220,#14532d);text-align:center;box-shadow:0 20px 44px -26px rgba(2,6,23,.6)}',
      '.blog-article .prose .dvb-mid h3{margin:0 0 8px;font-family:"Inter Tight",Inter,sans-serif;font-size:clamp(1.15rem,2.2vw,1.45rem);font-weight:800;color:#ffffff;line-height:1.3}',
      '.blog-article .prose .dvb-mid p{margin:0 0 18px;color:rgba(255,255,255,.82);font-size:.98rem;line-height:1.6}',
      '.blog-article .prose .dvb-mid a{display:inline-block;background:#22c55e;color:#06230f;font-weight:800;text-decoration:none;border-bottom:0;padding:13px 28px;border-radius:999px;font-size:1rem;transition:transform .15s,background .2s}',
      '.blog-article .prose .dvb-mid a:hover{transform:translateY(-1px);background:#4ade80;color:#06230f;text-decoration:none}',

      /* dark theme */
      '[data-theme="dark"] .dvb-form{background:#111827;border-color:#1e293b}',
      '[data-theme="dark"] .dvb-form h3{color:#f1f5f9}',
      '[data-theme="dark"] .dvb-f input,[data-theme="dark"] .dvb-f select,[data-theme="dark"] .dvb-f textarea{background:#0f172a;border-color:#1e293b;color:#e2e8f0}',
      '[data-theme="dark"] .dvb-trust{border-top-color:#1e293b}',

      /* tablet / mobile: single column, form moves BELOW the article so the post starts immediately */
      '@media(max-width:1024px){',
      '  .blog-article.dvb-on .container{max-width:760px}',
      '  .dvb-grid{grid-template-columns:1fr;gap:28px}',
      '  .dvb-side{position:static;order:2}',
      '  .dvb-main{order:1}',
      '}'
    ].join('\n');
    document.head.appendChild(s);
  }

  /* ---------------- markup ---------------- */
  function formHTML() {
    var opts = SERVICES.map(function (s) { return '<option value="' + esc(s) + '">' + esc(s) + '</option>'; }).join('');
    return '' +
      '<form class="dvb-form" novalidate>' +
        '<h3>Let’s Get Started</h3>' +
        '<p class="dvb-sub">Tell us what you need. A strategist replies within one business day.</p>' +
        '<div class="dvb-f"><input type="text" name="fullname" placeholder="Name*" autocomplete="name"></div>' +
        '<div class="dvb-f"><input type="email" name="email" placeholder="Email address*" autocomplete="email"></div>' +
        '<div class="dvb-f"><input type="tel" name="phone" placeholder="Phone number*" inputmode="numeric" maxlength="10" autocomplete="tel"></div>' +
        '<div class="dvb-f"><select name="service"><option value="">Interested Service</option>' + opts + '</select></div>' +
        '<div class="dvb-f"><textarea name="message" placeholder="Briefly describe your needs, i.e. brief your tentative start date, references, budgets, etc."></textarea></div>' +
        '<label class="dvb-consent"><input type="checkbox" checked><span>I agree to DigiVeritaz’s <a href="/terms-and-conditions/" target="_blank" rel="noopener">T&amp;C</a> and <a href="/privacy-policy/" target="_blank" rel="noopener">Privacy Policy</a>. This consent overrides any DNC/NDNC registration.</span></label>' +
        '<button class="dvb-btn" type="submit">Send</button>' +
        '<div class="dvb-err"></div>' +
        '<p class="dvb-trust">60+ brands · 1.15L+ leads delivered · 4–10× ROAS</p>' +
      '</form>';
  }

  function midHTML() {
    return '' +
      '<div class="dvb-mid">' +
        '<h3>Want this working for your brand?</h3>' +
        '<p>Get a free, tailored proposal — no obligation, delivered within one business day.</p>' +
        '<a href="/get-proposal/">Get My Free Proposal →</a>' +
      '</div>';
  }

  /* ---------------- lead save (same transport as the rest of the site) ---------------- */
  function saveLead(state) {
    try {
      var b = new URLSearchParams();
      b.set('action', 'lead_save');
      b.set('leadId', LEAD_ID);
      b.set('complete', '1');
      b.set('status', 'Complete');
      b.set('_source', 'blog-sidebar-form');
      b.set('_page', location.pathname || '/blog/');
      b.set('_subject', 'New lead from DigiVeritaz (blog form)');
      if (state.fullname) b.set('fullname', state.fullname);
      if (state.email) b.set('email', state.email);
      if (state.phone) b.set('phone', state.phone);
      if (state.message) b.set('message', state.message);
      if (state.consent) b.set('consent', state.consent);
      if (state.service) b.append('services[]', state.service);
      var ok = false;
      try {
        ok = !!(navigator.sendBeacon && navigator.sendBeacon(ENDPOINT,
          new Blob([b.toString()], { type: 'application/x-www-form-urlencoded;charset=UTF-8' })));
      } catch (e) {}
      if (!ok) { fetch(ENDPOINT, { method: 'POST', body: b, mode: 'no-cors', keepalive: true }).catch(function () {}); }
    } catch (e) {}
  }

  function wireForm(form) {
    var err = form.querySelector('.dvb-err');
    var btn = form.querySelector('.dvb-btn');
    var phone = form.querySelector('input[name=phone]');
    phone.addEventListener('input', function () { phone.value = phone.value.replace(/[^0-9]/g, '').slice(0, 10); });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var v = function (n) { var el = form.querySelector('[name=' + n + ']'); return el ? el.value.trim() : ''; };
      var name = v('fullname'), email = v('email'), ph = v('phone');
      var consent = form.querySelector('.dvb-consent input').checked;
      if (!name) { err.textContent = 'Please enter your name.'; return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { err.textContent = 'Please enter a valid email.'; return; }
      if (!/^[6-9][0-9]{9}$/.test(ph)) { err.textContent = 'Please enter a valid 10-digit mobile number.'; return; }
      if (!consent) { err.textContent = 'Please accept the T&C to continue.'; return; }
      err.textContent = '';
      btn.disabled = true; btn.textContent = 'Sending…';

      /* save FIRST — sendBeacon survives the redirect, so the Apps Script write and the
         automated email to the form filler are unaffected by the navigation below. */
      saveLead({ fullname: name, email: email, phone: ph, service: v('service'), message: v('message'), consent: consent ? 'Yes' : '' });
      try { (window.dataLayer = window.dataLayer || []).push({ event: 'lead_submitted', form_location: 'blog', lead_id: LEAD_ID }); } catch (e) {}
      setTimeout(function () {
        try { location.href = '/thank-you/?src=blog&lid=' + encodeURIComponent(LEAD_ID); } catch (e) {}
      }, 300);
    });
  }

  /* Keep the sticky sidebar clear of the sticky header. The header's offset and height
     both change across breakpoints (and the top contact bar may or may not be present),
     so measure instead of hard-coding: sticky-top = header's own top + its height + gap. */
  function syncStickyTop() {
    try {
      var h = document.querySelector('.site-header');
      if (!h) return;
      var top = parseFloat(getComputedStyle(h).top);
      if (isNaN(top)) top = 0;
      var height = h.getBoundingClientRect().height || 0;
      if (!height) return;
      document.documentElement.style.setProperty('--dvb-top', Math.round(top + height + 18) + 'px');
    } catch (e) {}
  }

  /* ---------------- inject ---------------- */
  function run() {
    var sec = document.querySelector('section.blog-article');
    if (!sec || sec.classList.contains('dvb-on')) return;
    var box = sec.querySelector('.container');
    var art = box && box.querySelector('article.prose');
    if (!box || !art) return;                       // not a blog post layout — bail safely

    css();

    /* 1. mid-article CTA: place before the H2 nearest the middle of the body */
    var hs = art.querySelectorAll('h2');
    if (hs.length >= 2) {
      var target = hs[Math.floor(hs.length / 2)];
      if (target) {
        var d = document.createElement('div');
        d.innerHTML = midHTML();
        target.parentNode.insertBefore(d.firstChild, target);
      }
    } else {
      var ps = art.querySelectorAll(':scope > p');
      if (ps.length >= 4) {
        var t2 = ps[Math.floor(ps.length / 2)];
        var d2 = document.createElement('div');
        d2.innerHTML = midHTML();
        t2.parentNode.insertBefore(d2.firstChild, t2);
      }
    }

    /* 2. re-flow into [ sidebar | article ] without destroying existing nodes */
    var grid = document.createElement('div');
    grid.className = 'dvb-grid';
    var side = document.createElement('aside');
    side.className = 'dvb-side';
    side.innerHTML = formHTML();
    var main = document.createElement('div');
    main.className = 'dvb-main';

    while (box.firstChild) { main.appendChild(box.firstChild); }   // move article + share row
    grid.appendChild(side);                                        // sidebar FIRST => left column
    grid.appendChild(main);
    box.appendChild(grid);
    sec.classList.add('dvb-on');

    wireForm(side.querySelector('.dvb-form'));

    syncStickyTop();
    /* re-measure once webfonts/layout settle, and whenever the breakpoint changes */
    setTimeout(syncStickyTop, 400);
    window.addEventListener('load', syncStickyTop);
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(syncStickyTop, 150); }, { passive: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
