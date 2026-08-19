// DigiVeritaz static site — minimal JS

/* ============================================================
   DV-ATTR v1 — campaign attribution for Google Ads / UTM tracking.
   Captures utm_* + gclid on the landing page and PERSISTS them, because a visitor
   usually arrives on a blog/landing page and submits somewhere else entirely
   (/get-proposal/, contact page) — without persistence the campaign is lost by
   the time the form is filled.
   Last-touch within a 90-day window: a fresh tagged click overwrites the stored
   set, so the campaign that actually drove the conversion gets the credit.
   Every form reads this via window.dvAttr() and posts it with the lead.
   ============================================================ */
;(function () {
  var KEY = 'dv-attr', MAX_AGE_DAYS = 90;
  /* gad_campaignid / gad_source / device come from Google Ads auto-tagging and are the
     reliable fallback when a ValueTrack placeholder like {campaignid} fails to resolve. */
  var FIELDS = ['utm_source','utm_medium','utm_campaign','utm_term','utm_content',
                'gclid','gbraid','wbraid','gad_campaignid','gad_source','device'];

  function read() {
    try {
      var raw = localStorage.getItem(KEY); if (!raw) return null;
      var o = JSON.parse(raw);
      if (!o || !o._at) return null;
      if (Date.now() - o._at > MAX_AGE_DAYS * 864e5) { localStorage.removeItem(KEY); return null; }
      return o;
    } catch (e) { return null; }
  }

  function capture() {
    try {
      var q = new URLSearchParams(location.search), found = {}, any = false;
      FIELDS.forEach(function (f) {
        var v = q.get(f);
        if (v) { found[f] = String(v).slice(0, 200); any = true; }
      });
      /* a bare gclid (auto-tagging, no utm_*) still means Google Ads */
      if (any) {
        if (!found.utm_source && (found.gclid || found.gbraid || found.wbraid || found.gad_campaignid)) {
          found.utm_source = 'google'; found.utm_medium = found.utm_medium || 'cpc';
        }
        /* An unresolved ValueTrack placeholder ('{campaignid}', '{keyword}' …) would otherwise
           be recorded verbatim on every lead. Substitute the real auto-tagged campaign id
           where we have it, and drop the placeholder where we don't. */
        ['utm_campaign','utm_term','utm_content','utm_source','utm_medium'].forEach(function (f) {
          if (found[f] && /^\{.*\}$/.test(found[f])) {
            if (f === 'utm_campaign' && found.gad_campaignid) found[f] = found.gad_campaignid;
            else delete found[f];
          }
        });
        found.landing_page = (location.pathname || '/') + (location.search || '');
        found.referrer = (document.referrer || '').slice(0, 300);
        found._at = Date.now();
        try { localStorage.setItem(KEY, JSON.stringify(found)); } catch (e) {}
        return found;
      }
      return read();
    } catch (e) { return null; }
  }

  var current = capture();

  /* Returns the stored campaign data (flat object) — {} when the visit is organic/direct. */
  window.dvAttr = function () {
    var o = current || read() || {};
    var out = {};
    FIELDS.concat(['landing_page','referrer']).forEach(function (f) { if (o[f]) out[f] = o[f]; });
    return out;
  };

  /* Carry the campaign THROUGH internal navigation instead of relying on storage alone.
     Clicking a link used to land on a bare URL with the params gone — they still
     resolved from localStorage, but that is invisible when debugging and is lost
     outright if storage is blocked (Safari private mode / ITP).

     NOTE: this is applied to all internal PAGE links (blog, services, conversion
     pages) because every page carries a CTA or a lead form. It is deliberately NOT
     applied to external hosts, mailto/tel, in-page anchors, or direct file links. */
  var CARRY = ['utm_source','utm_medium','utm_campaign','utm_term','utm_content',
               'gclid','gbraid','wbraid','gad_campaignid','device'];
  function decorate(link) {
    try {
      var o = current || read(); if (!o) return;
      var href = link.getAttribute('href');
      if (!href || href.charAt(0) === '#') return;
      if (/^(mailto:|tel:|javascript:|sms:|whatsapp:)/i.test(href)) return;
      var u = new URL(link.href, location.origin);
      if (u.host !== location.host) return;                       // never leak to third parties
      if (/\.[a-z0-9]{2,5}$/i.test(u.pathname) && !/\.html?$/i.test(u.pathname)) return;  // asset/file link
      var touched = false;
      CARRY.forEach(function (k) {
        if (o[k] && !u.searchParams.has(k)) { u.searchParams.set(k, o[k]); touched = true; }
      });
      if (touched) link.setAttribute('href', u.pathname + u.search + u.hash);
    } catch (e) {}
  }
  function decorateAll() {
    try { Array.prototype.forEach.call(document.querySelectorAll('a[href]'), decorate); } catch (e) {}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', decorateAll);
  else decorateAll();
  /* catch links added later (popups, injected CTAs) at click time */
  document.addEventListener('click', function (e) {
    var l = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (l) decorate(l);
  }, true);
})();

document.addEventListener('DOMContentLoaded', function () {
  // Scroll reveal
  var revealTargets = document.querySelectorAll('.reveal, section > .container > .section-head, section > .container > .panel, section .hero-grid > *, .svc-card, .wwd-card, .why-card, .tcard, .card, .rev-card');
  revealTargets.forEach(function (el) { el.classList.add('reveal'); });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
  }

  // Counter up
  var counters = document.querySelectorAll('[data-count]');
  var fmt = function (n) {
    if (n >= 100000) return (n / 1000).toFixed(0) + 'K';
    return String(n);
  };
  var runCounter = function (el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    var dur = 1400, start = performance.now();
    var tick = function (now) {
      var p = Math.min(1, (now - start) / dur);
      var val = Math.floor(target * (1 - Math.pow(1 - p, 3)));
      el.textContent = target >= 10000 ? fmt(val) : val;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if ('IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { runCounter(e.target); co.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { co.observe(c); });
  }

  // What We Do interactive index
  var wwdData = {
    seo: {
      num: '01', title: 'SEO &amp; Organic Growth',
      desc: 'Rank, engage and grow sustainably with technical SEO, content strategy and authority links that compound over time.',
      tags: ['Technical SEO','Content Strategy','Link Building','Local SEO'],
      cta: 'Explore SEO Services', href: 'seo.html',
      icon: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>'
    },
    paid: {
      num: '02', title: 'Paid Advertising',
      desc: 'From Meta to Google, we turn ad spend into profit with creative that stops the scroll and funnels that convert.',
      tags: ['Meta Ads','Google Ads','LinkedIn','Pinterest','Snapchat'],
      cta: 'Explore Paid Ads', href: 'paid-social-media-advertising.html',
      icon: '<svg viewBox="0 0 24 24"><path d="M3 6h14l4 4v6a2 2 0 0 1-2 2H3z"/><circle cx="8" cy="16" r="2"/><circle cx="17" cy="16" r="2"/></svg>'
    },
    perf: {
      num: '03', title: 'Performance Marketing',
      desc: 'Smart funnels, smarter conversions across search, display, shopping and video — fully attributed and reported.',
      tags: ['Search','Shopping','Display','Video','PMax'],
      cta: 'Explore Performance', href: 'performance-marketing-agency.html',
      icon: '<svg viewBox="0 0 24 24"><path d="M3 20h18"/><rect x="5" y="12" width="3" height="7" rx="1"/><rect x="11" y="8" width="3" height="11" rx="1"/><rect x="17" y="4" width="3" height="15" rx="1"/></svg>'
    },
    ecom: {
      num: '04', title: 'E-Commerce Management',
      desc: 'End-to-end Amazon, Flipkart and D2C growth — from listing optimization and ads to retention and loyalty.',
      tags: ['Amazon','Flipkart','Shopify','D2C','CRO'],
      cta: 'Explore E-Commerce', href: 'ecommerce-marketing.html',
      icon: '<svg viewBox="0 0 24 24"><path d="M3 7h15l-1.5 9A2 2 0 0 1 14.5 18h-8A2 2 0 0 1 4.5 16.3L3 7z"/><path d="M8 7V5a3 3 0 0 1 6 0v2"/></svg>'
    },
    wa: {
      num: '05', title: 'WhatsApp &amp; Native Ads',
      desc: 'Conversational commerce and premium native placements that drive direct response and high engagement.',
      tags: ['WhatsApp API','Swiggy','Zomato','Blinkit','Zepto'],
      cta: 'Explore WhatsApp', href: 'whatsapp-marketing-services.html',
      icon: '<svg viewBox="0 0 24 24"><path d="M4 11a8 8 0 1 1 3.5 6.6L3 19l1.4-4.2A7.9 7.9 0 0 1 4 11z"/></svg>'
    },
    brand: {
      num: '06', title: 'Branding &amp; Design',
      desc: 'Research-led branding, identity systems and creative direction that converts at every touchpoint.',
      tags: ['Strategy','Identity','Content','Creative','Web'],
      cta: 'Explore Branding', href: 'branding-and-design.html',
      icon: '<svg viewBox="0 0 24 24"><path d="M9 3l3 5 5 1-4 4 1 6-5-3-5 3 1-6-4-4 5-1z"/></svg>'
    }
  };
  var wwdList = document.getElementById('wwdList');
  var wwdPreview = document.getElementById('wwdPreview');
  if (wwdList && wwdPreview) {
    var renderPreview = function (key) {
      var d = wwdData[key]; if (!d) return;
      wwdPreview.innerHTML = '<div class="pv-icon">' + d.icon + '</div>'
        + '<div><div class="pv-eyebrow">Service ' + d.num + '</div>'
        + '<h3>' + d.title + '</h3>'
        + '<p>' + d.desc + '</p>'
        + '<div class="pv-tags">' + d.tags.map(function(t){return '<span>'+t+'</span>'}).join('') + '</div></div>'
        + '<a class="pv-cta" href="' + d.href + '">' + d.cta + '</a>';
      wwdPreview.classList.remove('wwd-fade');
      void wwdPreview.offsetWidth;
      wwdPreview.classList.add('wwd-fade');
    };
    var rows = wwdList.querySelectorAll('.wwd-row');
    var setActive = function (row) {
      rows.forEach(function (r) { r.classList.remove('active'); });
      row.classList.add('active');
      renderPreview(row.getAttribute('data-svc'));
    };
    rows.forEach(function (row) {
      row.addEventListener('mouseenter', function () { setActive(row); });
      row.addEventListener('click', function () {
        var d = wwdData[row.getAttribute('data-svc')];
        if (d) window.location.href = d.href;
      });
    });
  }

  // Theme toggle
  /* The homepage keeps its dark rules in a separate home-dark.min.css so the light-mode
     critical path stays small. index.html only document.write()s that file when
     localStorage ALREADY says dark, which meant a first-time click set data-theme="dark"
     against a stylesheet that had never been fetched — the toggle appeared dead until a
     reload. Fetch it on demand here, and only flip the attribute once it has actually
     loaded so there is no flash of half-themed page. Every other page ships its dark
     rules inside style.min.css, where there is no bundle link to find and this is a no-op. */
  function ensureDarkCss(done) {
    var bundle = document.querySelector('link[href*="home-bundle.min.css"]');
    if (!bundle) return done();                                             // not the homepage
    if (document.querySelector('link[href*="home-dark.min.css"]')) return done();  // already there
    var v = (bundle.getAttribute('href').match(/\?v=(\d+)/) || [])[1];      // track the bundle's cache-buster
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/css/home-dark.min.css' + (v ? '?v=' + v : '');
    var fired = false;
    var fire = function () { if (!fired) { fired = true; done(); } };
    link.onload = fire;
    link.onerror = fire;                       // still toggle if the file 404s
    setTimeout(fire, 1500);                    // never leave the button unresponsive
    document.head.appendChild(link);
  }

  var themeBtn = document.querySelector('.theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('dv-theme', next); } catch (e) {}
      if (next === 'dark') {
        ensureDarkCss(function () { document.documentElement.setAttribute('data-theme', 'dark'); });
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
    });
  }

  // Back-to-top button
  var top = document.querySelector('.to-top');
  if (top) {
    var toggleTop = function () { top.classList.toggle('show', window.scrollY > 400); };
    toggleTop();
    window.addEventListener('scroll', toggleTop, { passive: true });
    top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  // Scroll-state for floating header
  var hdr = document.querySelector('.site-header');
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle('scrolled', window.scrollY > 20); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Mobile nav toggle — hamburger morph, body scroll lock, backdrop, auto-close
  var hamb = document.querySelector('.hamb');
  var menu = document.querySelector('.nav ul');
  if (hamb && menu) {
    if (!hamb.querySelector('span')) hamb.appendChild(document.createElement('span'));
    hamb.setAttribute('aria-expanded', 'false');
    hamb.setAttribute('aria-controls', 'primary-nav-list');
    if (!menu.id) menu.id = 'primary-nav-list';

    var setNavOpen = function (open) {
      menu.classList.toggle('open', open);
      hamb.classList.toggle('is-open', open);
      hamb.setAttribute('aria-expanded', open ? 'true' : 'false');
      hamb.setAttribute('aria-label', open ? 'Close menu' : 'Menu');
      document.body.classList.toggle('nav-open', open);
    };

    hamb.addEventListener('click', function (e) {
      e.stopPropagation();
      setNavOpen(!menu.classList.contains('open'));
    });

    // close when tapping a real link (not the dropdown toggle)
    menu.querySelectorAll('a.navlink').forEach(function (a) {
      a.addEventListener('click', function () {
        if (a.closest('.has-dd') && window.matchMedia('(max-width: 960px)').matches) return;
        setNavOpen(false);
      });
    });
    menu.querySelectorAll('.dd-menu a').forEach(function (a) {
      a.addEventListener('click', function () { setNavOpen(false); });
    });

    // close on backdrop tap or Escape
    document.addEventListener('click', function (e) {
      if (!menu.classList.contains('open')) return;
      if (e.target.closest('.nav ul') || e.target.closest('.hamb')) return;
      setNavOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('open')) setNavOpen(false);
    });

    // close if resized back to desktop
    window.addEventListener('resize', function () {
      if (!window.matchMedia('(max-width: 1050px)').matches && menu.classList.contains('open')) {
        setNavOpen(false);
      }
    });
  }

  // Services dropdown — hover intent on desktop + tap-to-expand on mobile
  document.querySelectorAll('.has-dd').forEach(function (parent) {
    var link = parent.querySelector(':scope > .navlink');
    var hideTimer = null;
    var isMobile = function () { return window.matchMedia('(max-width: 960px)').matches; };

    // Mobile tap: toggle instead of navigating on first tap
    if (link) {
      link.addEventListener('click', function (e) {
        if (isMobile() && !parent.classList.contains('open')) {
          e.preventDefault();
          var navList = document.querySelector('.nav ul');
          var prevScroll = navList ? navList.scrollTop : 0;
          document.querySelectorAll('.has-dd.open').forEach(function (el) {
            if (el !== parent) el.classList.remove('open');
          });
          parent.classList.add('open');
          // Drop focus so the browser doesn't auto-scroll the parent item to the top
          if (link.blur) link.blur();
          if (navList) {
            // Pin the tapped item to the top of the drawer so its (long) submenu
            // reveals from its first item — otherwise the Services mega-menu opens
            // scrolled into the middle and the top services get cut off. Re-pin a
            // couple of times to win over the browser's late focus/anchor auto-scroll.
            var pin = function () {
              var r = parent.getBoundingClientRect(), c = navList.getBoundingClientRect();
              navList.scrollTop += r.top - c.top - 6;
            };
            requestAnimationFrame(pin);
            setTimeout(pin, 60);
            setTimeout(pin, 180);
          }
        }
      });
    }

    // Desktop hover: open instantly, close with 260ms grace so small cursor wobbles don't dismiss
    parent.addEventListener('mouseenter', function () {
      if (isMobile()) return;
      if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
      parent.classList.add('open');
    });
    parent.addEventListener('mouseleave', function () {
      if (isMobile()) return;
      if (hideTimer) clearTimeout(hideTimer);
      hideTimer = setTimeout(function () {
        parent.classList.remove('open');
        hideTimer = null;
      }, 260);
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-dd')) {
      document.querySelectorAll('.has-dd.open').forEach(function (el) { el.classList.remove('open'); });
    }
  });

  // Carousel pagination dots
  document.querySelectorAll('[data-carousel]').forEach(function (car) {
    var dots = car.parentElement.querySelector('[data-dots]');
    if (!dots) return;
    var updateDots = function () {
      var cards = car.children;
      if (!cards.length) return;
      var cardW = cards[0].getBoundingClientRect().width + 22;
      var visible = Math.max(1, Math.round(car.clientWidth / cardW));
      var pages = Math.max(1, cards.length - visible + 1);
      dots.innerHTML = '';
      for (var i = 0; i < pages; i++) dots.appendChild(document.createElement('i'));
      var idx = Math.round(car.scrollLeft / cardW);
      idx = Math.max(0, Math.min(pages - 1, idx));
      if (dots.children[idx]) dots.children[idx].classList.add('on');
    };
    updateDots();
    car.addEventListener('scroll', function () {
      var cards = car.children;
      if (!cards.length) return;
      var cardW = cards[0].getBoundingClientRect().width + 22;
      var idx = Math.round(car.scrollLeft / cardW);
      [].forEach.call(dots.children, function (d, i) { d.classList.toggle('on', i === idx); });
    }, { passive: true });
    window.addEventListener('resize', updateDots);
  });

  // FAQ accordion
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var q = item.querySelector('.faq-q');
    if (q) q.addEventListener('click', function () { item.classList.toggle('open'); });
  });

  // Contact form — submits to Google Apps Script (Sheet + email), with
  // FormSubmit.co as backup and mailto as last-resort fallback.
  var form = document.getElementById('contact-form');
  if (form && !document.getElementById('btn-send-otp')) {
    var CONTACT_EMAIL = 'info@digiveritaz.com';
    var APPS_SCRIPT_URL =
      'https://script.google.com/macros/s/AKfycby3DZjNUqSEU2Pg2rv45pnYTZT78L4405Et0SJ_NOBybsDLyd6ZWzxlSaEMx1TnKZkc/exec';

    var openMailtoFallback = function () {
      var fd = new FormData(form);
      var lines = [];
      fd.forEach(function (v, k) {
        if (k.charAt(0) === '_' || k === '_honey') return;
        if (!v) return;
        if (k === 'services[]') { lines.push('Service: ' + v); return; }
        var label = k.charAt(0).toUpperCase() + k.slice(1);
        lines.push(label + ': ' + v);
      });
      var subject = encodeURIComponent('New lead from DigiVeritaz website');
      var body = encodeURIComponent(lines.join('\n'));
      window.location.href = 'mailto:' + CONTACT_EMAIL + '?subject=' + subject + '&body=' + body;
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = (form.fullname && form.fullname.value || '').trim();
      var email = (form.email && form.email.value || '').trim();
      var phone = (form.phone && form.phone.value || '').trim();
      var ok = true;
      var errs = form.querySelectorAll('.error_frm');
      errs.forEach(function (el) { el.textContent = ''; });
      if (!name) { var en = form.querySelector('#error_fname'); if (en) en.textContent = 'Please enter your name'; ok = false; }
      if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        var ee = form.querySelector('#error_email'); if (ee) ee.textContent = 'Please enter a valid email'; ok = false;
      }
      if (!phone || phone.replace(/\D/g, '').length < 10) {
        var ep = form.querySelector('#error_phone'); if (ep) ep.textContent = 'Please enter a valid phone number'; ok = false;
      }
      if (!ok) return;

      var btn = form.querySelector('button[type=submit]');
      var origHTML = btn ? btn.innerHTML : '';
      if (btn) { btn.disabled = true; btn.innerHTML = 'Sending…'; }

      // Augment payload with referrer-style fields the Apps Script logs.
      var data = new FormData(form);
      data.append('_page', location.pathname || '/contact-us.html');
      data.append('_source', 'website-contact-form');

      // Primary endpoint: Google Apps Script Web App (writes to "DV Lead
      // Form" sheet + emails info@/daniel@/durvamukherjee@). We can't
      // read the response under no-cors but the POST does go through;
      // we'll trust it and redirect to the thank-you page.
      var appsScriptPromise = fetch(APPS_SCRIPT_URL, {
        method: 'POST',
        body: data,
        mode: 'no-cors',
        redirect: 'follow'
      });

      appsScriptPromise.then(function () {
        // Treat any successful network call as success — no-cors hides
        // the actual response status but the POST did reach Apps Script.
        window.location.href = '/thank-you/';
      }).catch(function () {
        // Apps Script unreachable — fall back to FormSubmit.co AJAX.
        fetch('https://formsubmit.co/ajax/' + CONTACT_EMAIL, {
          method: 'POST',
          headers: { 'Accept': 'application/json' },
          body: data
        }).then(function (res) {
          return res.json().then(function (j) { return { ok: res.ok, body: j }; });
        }).then(function (result) {
          if (result.ok && (result.body.success === 'true' || result.body.success === true)) {
            window.location.href = '/thank-you/';
          } else {
            if (btn) { btn.disabled = false; btn.innerHTML = origHTML; }
            openMailtoFallback();
          }
        }).catch(function () {
          if (btn) { btn.disabled = false; btn.innerHTML = origHTML; }
          openMailtoFallback();
        });
      });
    });
  }

  // Clients filter — pill tabs swap two opposite-moving marquees by category
  (function initClientFilter() {
    var filter = document.querySelector('.client-filter');
    var marquees = document.querySelectorAll('.client-marquee');
    var source = document.querySelector('[data-client-source]');
    if (!filter || marquees.length < 2 || !source) return;

    var MIN_VISIBLE_TILES = 12;   // ensure each row always feels full
    var TILE_WIDTH_PX = 268;      // 240px tile + 28px gap
    var SPEED_PX_PER_SEC = 55;    // visual scroll speed for all categories
    var allTiles = Array.prototype.slice.call(source.children);

    function buildTrack(track, items) {
      if (items.length === 0) { track.innerHTML = ''; track.style.animationDuration = ''; return; }
      var mult = Math.max(1, Math.ceil(MIN_VISIBLE_TILES / items.length));
      var expanded = [];
      for (var i = 0; i < mult; i++) {
        for (var j = 0; j < items.length; j++) expanded.push(items[j]);
      }
      var doubled = expanded.concat(expanded);
      track.innerHTML = '';
      doubled.forEach(function (tile) { track.appendChild(tile.cloneNode(true)); });
      // animation sweeps one copy (-50% of doubled track) → expanded.length tiles
      var halfWidth = expanded.length * TILE_WIDTH_PX;
      var duration = halfWidth / SPEED_PX_PER_SEC;
      track.style.animationDuration = duration.toFixed(1) + 's';
    }

    function build(filterKey) {
      var matches = allTiles.filter(function (t) {
        return filterKey === 'all' || t.getAttribute('data-category') === filterKey;
      });
      // split alternately into two rows for variety; reverse order on row B
      var rowA = [], rowB = [];
      matches.forEach(function (t, i) { (i % 2 === 0 ? rowA : rowB).push(t); });
      if (rowB.length === 0) rowB = rowA.slice().reverse();
      buildTrack(marquees[0].querySelector('[data-marquee-track]'), rowA);
      buildTrack(marquees[1].querySelector('[data-marquee-track]'), rowB);
    }

    function setFilter(key) {
      marquees.forEach(function (m) { m.classList.add('is-swapping'); });
      setTimeout(function () {
        build(key);
        requestAnimationFrame(function () {
          marquees.forEach(function (m) { m.classList.remove('is-swapping'); });
        });
      }, 200);
    }

    filter.addEventListener('click', function (e) {
      var btn = e.target.closest('.pill');
      if (!btn || btn.classList.contains('is-active')) return;
      filter.querySelectorAll('.pill').forEach(function (p) {
        p.classList.remove('is-active');
        p.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('is-active');
      btn.setAttribute('aria-selected', 'true');
      setFilter(btn.getAttribute('data-filter'));
    });

    build('all');
  })();
});
/* DV-POPUP v3 (abhishek-edits): "Lets Get Project Started" — the WIDE popup that
   AUTO-OPENS once per session (3s, desktop only). It is NOT wired to any CTA.
   All CTAs open the separate "Get Your Free Proposal" phone popup (dv-lead.js),
   which this file loads. Phone OTP via MSG91 ("Get OTP" beside the phone; Submit
   unlocks only after the number is verified). Saves to Apps Script (lead_save). */
;(function(){
  if (window.__dvmInit) return; window.__dvmInit = true;
  var ENDPOINT = 'https://script.google.com/macros/s/AKfycby3DZjNUqSEU2Pg2rv45pnYTZT78L4405Et0SJ_NOBybsDLyd6ZWzxlSaEMx1TnKZkc/exec';
  var MSG91 = { widgetId: '3666766e6633313737383230', tokenAuth: '520932TU9OQwuB86a3942beP1' };
  var DVM_LOAD = Date.now();
  var SERVICES = [
    ['Organic Marketing','Organic Marketing'],
    ['Paid Social Media','Paid Social Media Advertising'],
    ['PPC','Pay-Per-Click Advertising'],
    ['Performance Marketing','Performance Marketing'],
    ['E-commerce','E-commerce Platforms'],
    ['Data Strategy','Data Strategy & Consulting'],
    ['Native Advertising','Native Advertising'],
    ['WhatsApp','WhatsApp Marketing'],
    ['Branding','Branding & Design'],
    ['SEO','Search Engine Optimization'],
    ['GSO','Generative Search Optimisation'],
    ['Tech & Development','Tech & Development']
  ];
  var ready=false, verified=false, sent=false, dvmLeadId='', warmed=false;
  function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function $(id){ return document.getElementById(id); }
  var OTPBTN='flex:0 0 auto;white-space:nowrap;background:#22c55e;color:#fff;border:0;padding:0 14px;border-radius:10px;font-weight:700;cursor:pointer;font-size:.85rem';
  var OTPINP='flex:1 1 auto;padding:11px 12px;border:1.5px solid #e5e7eb;border-radius:10px;font-size:1rem;text-align:center;letter-spacing:.2em';

  function buildModal(){
    if ($('dvm-overlay')) return;
    var checks = SERVICES.map(function(s){ return '<label><input type="checkbox" name="services[]" value="'+esc(s[0])+'">'+esc(s[1])+'</label>'; }).join('');
    var html = ''
      +'<div class="dvm-card" role="document">'
      +'<button class="dvm-close" type="button" aria-label="Close">&times;</button>'
      +'<h2 class="dvm-title">Lets Get Project Started</h2>'
      +'<p class="dvm-sub">Share your goals, budget and timeline &mdash; we&rsquo;ll send a tailored proposal within one business day.</p>'
      +'<form id="dvm-form" class="dvm-form" novalidate>'
      +'<input type="hidden" name="_subject" value="New lead from DigiVeritaz (popup)">'
      +'<input type="hidden" name="_template" value="table">'
      +'<input type="hidden" name="_captcha" value="false">'
      +'<div class="dvm-hp" aria-hidden="true" style="position:absolute;left:-9999px"><label>Leave this empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label><label>Do not fill<input type="text" name="_hp_site" tabindex="-1" autocomplete="off"></label><label>Do not fill<input type="text" name="_hp_addr" tabindex="-1" autocomplete="off"></label></div>'
      +'<input type="hidden" name="_ts" id="dvm-ts"><input type="hidden" name="_jsok" id="dvm-jsok">'
      +'<div class="dvm-row">'
      +'<div class="dvm-field"><label>Full Name <span class="req">*</span></label><input type="text" name="fullname" placeholder="Your full name" required></div>'
      +'<div class="dvm-field"><label>Email Address <span class="req">*</span></label><input type="email" name="email" placeholder="you@company.com" required></div>'
      +'<div class="dvm-field"><label>Phone Number <span class="req">*</span></label><div style="display:flex;gap:8px;align-items:stretch"><input type="tel" name="phone" id="dvm-phone" placeholder="+91 9XXXXXXXXX" required style="flex:1 1 auto"><button type="button" id="dvm-getotp" style="'+OTPBTN+'">Get OTP</button></div><div id="dvm-otp-row" style="display:none;gap:8px;align-items:stretch;margin-top:8px"><input type="text" id="dvm-otp" inputmode="numeric" maxlength="6" autocomplete="one-time-code" placeholder="6-digit OTP" style="'+OTPINP+'"><button type="button" id="dvm-verify" style="'+OTPBTN+';background:#0f2a5a">Verify</button></div><div id="dvm-otp-msg" style="font-size:.82rem;margin-top:6px;min-height:1em"></div></div>'
      +'</div>'
      +'<div class="dvm-row">'
      +'<div class="dvm-field"><label>Company Name</label><input type="text" name="company" placeholder="Company"></div>'
      +'<div class="dvm-field col2"><label>Budget Range <span class="req">*</span></label><select name="budget" required><option value="">-- Please select budget range --</option><option>INR 40k &ndash; 60k</option><option>INR 60k to 1 Lac</option><option>INR 1 Lac and above</option></select></div>'
      +'</div>'
      +'<div class="dvm-seclabel">Select the Services You Need</div>'
      +'<div class="dvm-checks">'+checks+'</div>'
      +'<div class="dvm-field full" style="margin-bottom:14px"><label>Project Brief</label><textarea name="message" rows="2" placeholder="Tentative start date, goals, platforms of interest&hellip;"></textarea></div>'
      +'<button class="dvm-send" type="submit" id="dvm-submit" disabled style="opacity:.5">Submit</button>'
      +'<div class="dvm-msg" id="dvm-msg" style="text-align:center;margin-top:10px"></div>'
      +'</form>'
      +'</div>';
    var ov = document.createElement('div');
    ov.className = 'dvm-overlay'; ov.id = 'dvm-overlay';
    ov.setAttribute('role','dialog'); ov.setAttribute('aria-modal','true'); ov.setAttribute('aria-label','Start your project'); ov.setAttribute('aria-hidden','true');
    ov.innerHTML = html;
    document.body.appendChild(ov);
    ov.querySelector('.dvm-close').addEventListener('click', closeModal);
    ov.addEventListener('mousedown', function(e){ if (e.target === ov) closeModal(); });
    wireForm();
  }

  function omsg(t,c){ var m=$('dvm-otp-msg'); if(m){ m.textContent=t||''; m.style.color=c||'#475569'; } }
  function fmsg(t,c){ var m=$('dvm-msg'); if(m){ m.textContent=t||''; m.style.color=c||'#475569'; } }
  function digits(){ var p=$('dvm-phone'); return ((p&&p.value)||'').replace(/[^0-9]/g,'').slice(-10); }
  function phoneOk(){ return /^[6-9][0-9]{9}$/.test(digits()); }
  function emailOk(v){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v||'').trim()); }
  function setSubmit(){ var b=$('dvm-submit'); if(b){ b.disabled=!verified; b.style.opacity=verified?'1':'.5'; } }

  function initMsg91(){ if(ready) return true; if(typeof window.sendOtp==='function'){ ready=true; return true; } if(typeof window.initSendOTP!=='function') return false; try{ window.initSendOTP({widgetId:MSG91.widgetId,tokenAuth:MSG91.tokenAuth,exposeMethods:true,success:function(){},failure:function(){}}); ready=true; }catch(e){} return ready; }
  function loadMsg91(cb){ if(initMsg91()){ cb(true); return; } if(loadMsg91._loading){ loadMsg91._q.push(cb); return; } loadMsg91._loading=true; loadMsg91._q=[cb]; var urls=['https://verify.msg91.com/otp-provider.js','https://verify.phone91.com/otp-provider.js'], i=0; function done(ok){ loadMsg91._loading=false; var q=loadMsg91._q; loadMsg91._q=[]; q.forEach(function(fn){ try{ fn(ok); }catch(e){} }); } (function go(){ if(typeof window.initSendOTP==='function'){ done(initMsg91()); return; } var s=document.createElement('script'); s.src=urls[i]; s.async=true; s.onload=function(){ done(initMsg91()); }; s.onerror=function(){ i++; if(i<urls.length) go(); else done(false); }; document.head.appendChild(s); })(); }
  function warmMsg91(){ if(warmed) return; warmed=true; try{ loadMsg91(function(){}); }catch(e){} }

  function doSend(isResend){
    if(!phoneOk()){ omsg('Enter a valid 10-digit mobile number.','#dc2626'); return; }
    if(!isResend) saveLead(false);   /* capture the number as a Partial lead before OTP */
    var g=$('dvm-getotp'); if(g) g.disabled=true; omsg(isResend?'Sending a new code…':'Sending OTP…');
    loadMsg91(function(ok){
      if(!ok || typeof window.sendOtp!=='function'){ if(g) g.disabled=false; omsg('Could not reach the OTP service. Please try again.','#dc2626'); return; }
      var onSent=function(){ sent=true; if(g){ g.disabled=false; g.textContent='Resend'; } var r=$('dvm-otp-row'); if(r) r.style.display='flex'; omsg('OTP sent to +91 '+digits()+' via SMS.','#16a34a'); var oi=$('dvm-otp'); if(oi){ try{oi.focus();}catch(e){} } };
      var onErr=function(err){ if(g) g.disabled=false; try{console.error('MSG91 sendOtp',err);}catch(e){} omsg('Could not send OTP — check the number and try again.','#dc2626'); };
      if(isResend && window.retryOtp){ window.retryOtp(null,onSent,onErr); } else { window.sendOtp('91'+digits(),onSent,onErr); }
    });
  }
  function doVerify(){
    var oi=$('dvm-otp'); var code=((oi&&oi.value)||'').replace(/[^0-9]/g,'');
    if(code.length<4){ omsg('Enter the code from the SMS.','#dc2626'); return; }
    if(typeof window.verifyOtp!=='function'){ omsg('Verification not ready — resend the code.','#dc2626'); return; }
    var v=$('dvm-verify'); if(v) v.disabled=true; omsg('Verifying…');
    window.verifyOtp(code, function(){ verified=true; if(v) v.disabled=false; var r=$('dvm-otp-row'); if(r) r.style.display='none'; var g=$('dvm-getotp'); if(g){ g.textContent='Verified ✓'; g.disabled=true; g.style.background='#16a34a'; } var p=$('dvm-phone'); if(p) p.readOnly=true; omsg('Mobile number verified ✓','#16a34a'); setSubmit(); fmsg(''); }, function(err){ if(v) v.disabled=false; try{console.error('MSG91 verifyOtp',err);}catch(e){} omsg('Incorrect or expired code. Resend and try again.','#dc2626'); });
  }
  function collect(){ var form=$('dvm-form'); var fd=new FormData(form), o={}; fd.forEach(function(v,k){ if(o[k]!==undefined){ if(!Array.isArray(o[k])) o[k]=[o[k]]; o[k].push(v); } else o[k]=v; }); return o; }
  function sendLead(payload){ var b=new URLSearchParams(); Object.keys(payload).forEach(function(k){ var v=payload[k]; if(Array.isArray(v)) v.forEach(function(x){ b.append(k,x); }); else if(v!=null) b.append(k,String(v)); }); try{var _a=(typeof window.dvAttr==='function')?window.dvAttr():{};for(var _k in _a){if(_a[_k])b.set(_k,_a[_k]);}}catch(e){} var ok=false; try{ ok=!!(navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, new Blob([b.toString()],{type:'application/x-www-form-urlencoded;charset=UTF-8'}))); }catch(e){} if(!ok){ fetch(ENDPOINT,{method:'POST',body:b,mode:'no-cors',keepalive:true}).catch(function(){}); } }

  function saveLead(complete){
    var d=collect();
    var payload=Object.assign({}, d, {
      action:'lead_save', leadId: dvmLeadId,
      otp_verified: verified ? 'yes' : '',
      status: complete ? 'Complete' : 'Partial',
      complete: complete ? '1' : '',
      _source:'website-popup-form', _page:(location.pathname||'/'),
      _subject: complete ? 'New lead from DigiVeritaz (popup)' : 'New lead (number captured) — DigiVeritaz'
    });
    delete payload.otp;
    sendLead(payload);
  }
  function onSubmit(ev){
    ev.preventDefault();
    var d=collect();
    if(!d.fullname){ fmsg('Please enter your name.','#dc2626'); return; }
    if(!emailOk(d.email)){ fmsg('Please enter a valid email.','#dc2626'); return; }
    if(!phoneOk()){ fmsg('Please enter a valid 10-digit phone number.','#dc2626'); return; }
    if(!d.budget){ fmsg('Please select a budget range.','#dc2626'); return; }
    if(!verified){ fmsg('Please verify your mobile number with the OTP first.','#dc2626'); return; }
    var b=$('dvm-submit'); if(b){ b.disabled=true; b.style.opacity='.6'; } fmsg('Submitting…');
    saveLead(true);
    dvmFinish();
  }
  function dvmFinish(){
    var card=document.querySelector('#dvm-overlay .dvm-card');
    if(card){ card.innerHTML = '<button class="dvm-close" type="button" aria-label="Close">&times;</button><div class="dvm-thanks" style="text-align:center;padding:34px 12px"><h3 style="color:#0f2a5a;margin:0 0 10px">Thank you!</h3><p style="color:#64748b">We&rsquo;ve received your details &mdash; taking you to your confirmation&hellip;</p></div>'; card.querySelector('.dvm-close').addEventListener('click', closeModal); }
    /* saveLead(true) already ran and uses sendBeacon/keepalive, so the lead write and
       the automated email survive this navigation. Redirect so the conversion is
       tracked on the dedicated /thank-you/ URL. */
    try { (window.dataLayer = window.dataLayer || []).push({ event:'lead_submitted', form_location:'popup', lead_id: dvmLeadId }); } catch(e){}
    setTimeout(function(){ try { window.location.href = '/thank-you/?src=popup&lid=' + encodeURIComponent(dvmLeadId); } catch(e){} }, 400);
  }

  function wireForm(){
    var f=$('dvm-form'); if(f) f.addEventListener('submit', onSubmit);
    var g=$('dvm-getotp'); if(g) g.addEventListener('click', function(){ doSend(sent); });
    var v=$('dvm-verify'); if(v) v.addEventListener('click', doVerify);
    var p=$('dvm-phone'); if(p) p.addEventListener('input', function(){ if(verified){ verified=false; setSubmit(); } });
    var oi=$('dvm-otp'); if(oi) oi.addEventListener('input', function(){ oi.value=oi.value.replace(/[^0-9]/g,'').slice(0,6); });
    setSubmit();
  }

  function openModal(){
    buildModal();
    warmMsg91();   /* preload + init MSG91 on open so window.sendOtp is ready before "Get OTP" is clicked */
    if(!dvmLeadId) dvmLeadId='dvm-'+DVM_LOAD.toString(36)+'-'+Math.random().toString(36).slice(2,8);
    var ov=$('dvm-overlay'); if(!ov) return;
    var ts=$('dvm-ts'), js=$('dvm-jsok');
    if(ts) ts.value=String(DVM_LOAD);
    if(js) js.value='dv-'+Math.random().toString(36).slice(2,12);
    ov.classList.add('is-open'); ov.setAttribute('aria-hidden','false');
    document.body.classList.add('dvm-lock');
    var fn=ov.querySelector('input[name=fullname]'); if(fn){ try{ fn.focus(); }catch(e){} }
  }
  function closeModal(){ var ov=$('dvm-overlay'); if(!ov) return; ov.classList.remove('is-open'); ov.setAttribute('aria-hidden','true'); document.body.classList.remove('dvm-lock'); }
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeModal(); });

  /* CTAs are NOT wired to this wide popup. They open the "Get Your Free Proposal"
     phone popup, handled by dv-lead.js — which we load here on every page. */
  function loadDvLead(){ if (window.__dvLeadV2 || document.getElementById('dvlead-js')) return; var s=document.createElement('script'); s.id='dvlead-js'; s.src='/js/dv-lead.min.js?v=1788800000'; document.head.appendChild(s); }

  /* Blog posts get the sidebar lead form + mid-article CTA. Loaded here (not hard-coded
     into each post) so all existing AND all future blog pages pick it up automatically. */
  function loadBlogCta(){
    if (!/^\/blog\/[^/]+\/?$/.test(location.pathname)) return;   // posts only, not /blog/ index
    if (window.__dvBlogCta || document.getElementById('dvblogcta-js')) return;
    var s=document.createElement('script'); s.id='dvblogcta-js'; s.src='/js/blog-cta.min.js?v=1786000000'; document.head.appendChild(s);
  }

  function isDesktop(){ return window.matchMedia ? window.matchMedia('(min-width: 1024px)').matches : (window.innerWidth>=1024); }
  function dvReady(){
    loadDvLead();
    loadBlogCta();
    /* the WIDE popup only auto-opens once (3s, desktop, not on contact/proposal pages) */
    try {
      if (isDesktop() && !/\/(contact-us|get-proposal|careers)(\/|\.html|$)/.test(location.pathname) && !sessionStorage.getItem('dvmSeen')) {
        setTimeout(function(){ try{ sessionStorage.setItem('dvmSeen','1'); }catch(e){} openModal(); }, 3000);
      }
    } catch(e){}
  }
  if (document.readyState !== 'loading') dvReady();
  else document.addEventListener('DOMContentLoaded', dvReady);
})();
/* DV-TOPBAR v1 (abhishek-edits): inject sticky top contact bar (WhatsApp / Phone / Email) */
;(function(){
  if (window.__dvTopbar) return; window.__dvTopbar = true;
  var WA = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.5 3.5A11.4 11.4 0 0 0 12 0C5.5 0 .2 5.3.2 11.8c0 2.1.5 4.1 1.6 5.9L0 24l6.4-1.7c1.7.9 3.6 1.4 5.6 1.4 6.5 0 11.8-5.3 11.8-11.8 0-3.2-1.2-6.1-3.3-8.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4a9.7 9.7 0 0 1-1.5-5.4C2.2 6.4 6.6 2 12 2s9.8 4.4 9.8 9.8-4.4 10-9.8 10zm5.4-7.3c-.3-.1-1.7-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.7 1-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.2-.5-2.3-1.4-.9-.8-1.4-1.7-1.6-2-.2-.3 0-.5.1-.6l.4-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.5-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.2 5 4.5.7.3 1.3.5 1.7.6.7.2 1.3.2 1.8.1.6-.1 1.7-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.2-.6-.4z"/></svg>';
  var PH = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.5 15.5 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24 11.4 11.4 0 0 0 3.6.58 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .6 3.6 1 1 0 0 1-.25 1l-2.2 2.2z"/></svg>';
  var EM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>';

  function build(){
    if (document.querySelector('.dv-topbar')) return;
    var bar = document.createElement('div');
    bar.className = 'dv-topbar';
    bar.innerHTML = '<div class="dv-tb-inner">'
      + '<a class="dv-tb-item dv-tb-wa" href="https://wa.me/919956655662" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">' + WA + '+91 99566 55662</a>'
      + '<a class="dv-tb-item dv-tb-ph" href="tel:+919956655662" aria-label="Call us">' + PH + '+91 99566 55662</a>'
      + '<a class="dv-tb-item dv-tb-em" href="mailto:info@digiveritaz.com" aria-label="Email us">' + EM + 'info@digiveritaz.com</a>'
      + '</div>';
    var header = document.querySelector('header.site-header');
    if (header && header.parentNode) header.parentNode.insertBefore(bar, header);
    else document.body.insertBefore(bar, document.body.firstChild);
  }
  if (document.readyState !== 'loading') build();
  else document.addEventListener('DOMContentLoaded', build);
})();
/* DV-MOBILE v1 (abhishek-edits): mobile sticky Book-a-Call + Live Chat bar + WhatsApp float */
;(function(){
  if (window.__dvMobile) return; window.__dvMobile = true;
  var WA = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.5 3.5A11.4 11.4 0 0 0 12 0C5.5 0 .2 5.3.2 11.8c0 2.1.5 4.1 1.6 5.9L0 24l6.4-1.7c1.7.9 3.6 1.4 5.6 1.4 6.5 0 11.8-5.3 11.8-11.8 0-3.2-1.2-6.1-3.3-8.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4a9.7 9.7 0 0 1-1.5-5.4C2.2 6.4 6.6 2 12 2s9.8 4.4 9.8 9.8-4.4 10-9.8 10zm5.4-7.3c-.3-.1-1.7-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.7 1-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.2-.5-2.3-1.4-.9-.8-1.4-1.7-1.6-2-.2-.3 0-.5.1-.6l.4-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.5-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.2 5 4.5.7.3 1.3.5 1.7.6.7.2 1.3.2 1.8.1.6-.1 1.7-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.2-.6-.4z"/></svg>';
  var CHAT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9.1 9.1 0 0 1-3.3-.6L3 21l1.3-4a8.2 8.2 0 0 1-1-4 8.4 8.4 0 0 1 9-8.4 8.4 8.4 0 0 1 8.7 7.4z"/></svg>';

  function toast(msg){
    var t = document.querySelector('.dv-mtoast');
    if (!t){ t = document.createElement('div'); t.className = 'dv-mtoast'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(t._h); t._h = setTimeout(function(){ t.classList.remove('show'); }, 2200);
  }

  function build(){
    if (document.querySelector('.dv-mbar')) return;
    var bar = document.createElement('div');
    bar.className = 'dv-mbar';
    bar.innerHTML = '<button type="button" class="dv-m-call">Book a Call</button>'
      + '<button type="button" class="dv-m-chat">' + CHAT + 'Live Chat</button>';
    document.body.appendChild(bar);

    var wa = document.createElement('a');
    wa.className = 'dv-wafloat';
    wa.href = 'https://wa.me/919956655662';
    wa.target = '_blank'; wa.rel = 'noopener';
    wa.setAttribute('aria-label', 'Chat on WhatsApp');
    wa.innerHTML = WA;
    document.body.appendChild(wa);

    bar.querySelector('.dv-m-call').addEventListener('click', function(){
      if (typeof window.dvOpenModal === 'function') window.dvOpenModal();
      else window.location.href = '/contact-us/';
    });
    bar.querySelector('.dv-m-chat').addEventListener('click', function(){
      if (typeof window.dvOpenChat === 'function') window.dvOpenChat();
      else toast('Live chat is coming soon!');
    });
  }
  if (document.readyState !== 'loading') build();
  else document.addEventListener('DOMContentLoaded', build);
})();

/* DV-CHATBOT v1 — lead-qualification chat widget (talks to /api/chat) */
;(function(){
  if (window.__dvChat) return; window.__dvChat = true;
  var WA = "https://wa.me/919956655662";
  var BOOK = "/contact-us/";
  var GREETING = "Hi! 👋 I'm Veri from DigiVeritaz. What are you trying to achieve — more leads, better ROAS, or something else? I can point you to the right service and set up a quick call.";
  var I_CHAT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9.1 9.1 0 0 1-3.3-.6L3 21l1.3-4a8.2 8.2 0 0 1-1-4 8.4 8.4 0 0 1 9-8.4 8.4 8.4 0 0 1 8.7 7.4z"/></svg>';
  var I_SEND = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.4 20.4l17.5-7.5a1 1 0 0 0 0-1.8L3.4 3.6a1 1 0 0 0-1.4 1l2 6.9 9 1.5-9 1.5-2 6.9a1 1 0 0 0 1.4 1z"/></svg>';
  var I_WA = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 3.5A11.4 11.4 0 0 0 12 0C5.5 0 .2 5.3.2 11.8c0 2.1.5 4.1 1.6 5.9L0 24l6.4-1.7c1.7.9 3.6 1.4 5.6 1.4 6.5 0 11.8-5.3 11.8-11.8 0-3.2-1.2-6.1-3.3-8.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4a9.7 9.7 0 0 1-1.5-5.4C2.2 6.4 6.6 2 12 2s9.8 4.4 9.8 9.8-4.4 10-9.8 10z"/></svg>';
  var I_CAL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>';

  var msgs = [];
  try { msgs = JSON.parse(sessionStorage.getItem("dvc-msgs") || "[]"); } catch (e) { msgs = []; }
  var launch, panel, body, ta;

  function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function linkify(t){
    return esc(t).replace(/(https?:\/\/[^\s]+|\/[a-z0-9][a-z0-9\-\/]*\/)/gi, function(u){
      var ext = u.indexOf("http") === 0;
      return '<a href="' + u + '"' + (ext ? ' target="_blank" rel="noopener"' : '') + '>' + u + '</a>';
    });
  }
  function save(){ try { sessionStorage.setItem("dvc-msgs", JSON.stringify(msgs.slice(-30))); } catch (e) {} }

  function addMsg(role, text, services){
    var m = document.createElement("div");
    m.className = "dvc-msg " + (role === "user" ? "dvc-user" : "dvc-bot");
    m.innerHTML = linkify(text);
    body.appendChild(m);
    if (role !== "user" && services && services.length){
      var sc = document.createElement("div"); sc.className = "dvc-svcs";
      sc.innerHTML = services.map(function(s){ return '<a class="dvc-svc" href="' + s.url + '">' + esc(s.label) + '</a>'; }).join("");
      body.appendChild(sc);
    }
    body.scrollTop = body.scrollHeight;
  }
  function typing(on){
    var t = document.getElementById("dvc-typing");
    if (on && !t){
      t = document.createElement("div"); t.id = "dvc-typing"; t.className = "dvc-typing";
      t.innerHTML = "<span></span><span></span><span></span>";
      body.appendChild(t); body.scrollTop = body.scrollHeight;
    } else if (!on && t){ t.remove(); }
  }

  function send(){
    var v = ta.value.trim(); if (!v) return;
    ta.value = ""; ta.style.height = "42px";
    msgs.push({ role: "user", content: v }); addMsg("user", v); save();
    typing(true);
    fetch("/api/chat/", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ page: location.pathname, messages: msgs })
    }).then(function(r){ return r.json(); }).then(function(d){
      typing(false);
      var rep = (d && d.reply) || "Sorry, please try again.";
      var svcs = (d && d.services) || [];
      msgs.push({ role: "assistant", content: rep, services: svcs }); addMsg("assistant", rep, svcs); save();
      /* The chatbot captures OTP-verified leads server-side (api/chat.py -> Apps Script)
         and already returns d.captured. Fire the conversion here — we deliberately do NOT
         redirect, because yanking the user out of an open conversation would be hostile. */
      if (d && d.captured && !window.__dvChatLeadTracked) {
        window.__dvChatLeadTracked = true;
        try { (window.dataLayer = window.dataLayer || []).push({ event:'lead_submitted', form_location:'chatbot' }); } catch(e){}
        try { if (typeof window.gtag === 'function') window.gtag('event','generate_lead',{ form_location:'chatbot' }); } catch(e){}
      }
    }).catch(function(){
      typing(false);
      addMsg("assistant", "I'm having a connection issue — please WhatsApp us at +91 99566 55662 and the team will help right away.");
    });
  }

  function build(){
    launch = document.createElement("button");
    launch.className = "dvc-launch"; launch.setAttribute("aria-label", "Chat with DigiVeritaz");
    launch.innerHTML = I_CHAT + '<span class="dvc-lbl">Chat with us</span>';
    document.body.appendChild(launch);

    panel = document.createElement("div");
    panel.className = "dvc-panel"; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", "DigiVeritaz chat");
    panel.innerHTML =
      '<div class="dvc-head"><img src="/assets/logo.webp" alt="DigiVeritaz">' +
        '<div class="ht"><span class="t">DigiVeritaz</span><span class="s"><span class="dot"></span>Usually replies instantly</span></div>' +
        '<button class="dvc-x" aria-label="Close">&times;</button></div>' +
      '<div class="dvc-body" id="dvc-body"></div>' +
      '<div class="dvc-chips">' +
        '<a class="dvc-chip" href="' + WA + '" target="_blank" rel="noopener">' + I_WA + 'WhatsApp</a>' +
        '<a class="dvc-chip dvc-book" href="' + BOOK + '">' + I_CAL + 'Book a call</a>' +
      '</div>' +
      '<div class="dvc-foot"><textarea id="dvc-ta" rows="1" placeholder="Type your message…"></textarea>' +
        '<button class="dvc-send" id="dvc-send" aria-label="Send">' + I_SEND + '</button></div>';
    document.body.appendChild(panel);

    body = panel.querySelector("#dvc-body");
    ta = panel.querySelector("#dvc-ta");

    launch.addEventListener("click", open);
    panel.querySelector(".dvc-x").addEventListener("click", close);
    panel.querySelector("#dvc-send").addEventListener("click", send);
    var _bk = panel.querySelector(".dvc-book");
    if (_bk) _bk.addEventListener("click", function(e){ if (typeof window.dvOpenModal === "function"){ e.preventDefault(); close(); window.dvOpenModal(); } });
    ta.addEventListener("keydown", function(e){ if (e.key === "Enter" && !e.shiftKey){ e.preventDefault(); send(); } });
    ta.addEventListener("input", function(){ ta.style.height = "42px"; ta.style.height = Math.min(96, ta.scrollHeight) + "px"; });
  }

  function open(){
    panel.classList.add("open"); launch.style.display = "none";
    if (!body.childElementCount){
      if (!msgs.length){ msgs.push({ role: "assistant", content: GREETING }); save(); }
      msgs.forEach(function(m){ addMsg(m.role, m.content, m.services); });
    }
    setTimeout(function(){ ta.focus(); }, 50);
  }
  function close(){ panel.classList.remove("open"); launch.style.display = "flex"; }
  window.dvOpenChat = function(){ if (panel) open(); };

  if (document.readyState !== "loading") build();
  else document.addEventListener("DOMContentLoaded", build);
})();
/* DV-SEARCH v1 — header site search.
   Injects an icon-only button immediately to the LEFT of the "Book A Call" CTA. Clicking it
   expands the pill into an input; typing filters a lazily-fetched index of every page and its
   sections. The index (/search-index.json) is only fetched on first open, so pages that never
   use search pay nothing for it. */
;(function(){
  if (window.__dvSearch) return; window.__dvSearch = true;

  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/></svg>';
  var XICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>';
  var MAX_PAGES = 12, MAX_HITS_PER_PAGE = 3;

  var idx = null, loading = false, wrap, btn, input, clear, panel, sel = -1;

  /* ---------- matching ---------- */
  function norm(s){
    return String(s || '').toLowerCase()
      .replace(/[‘’“”]/g, "'")
      .replace(/[^a-z0-9'\s-]/g, ' ')
      .replace(/\s+/g, ' ').trim();
  }
  function tokens(q){ return norm(q).split(' ').filter(Boolean); }

  /* True when a and b differ by at most one edit (substitute / insert / delete). */
  function within1(a, b){
    if (Math.abs(a.length - b.length) > 1) return false;
    var i = 0, j = 0, diff = 0;
    while (i < a.length && j < b.length){
      if (a[i] === b[j]){ i++; j++; continue; }
      if (++diff > 1) return false;
      if (a.length > b.length) i++;
      else if (b.length > a.length) j++;
      else { i++; j++; }
    }
    return diff + (a.length - i) + (b.length - j) <= 1;
  }

  /* Matching is word-aware, in tiers, because plain substring matching is far too loose:
       any length : the token must at least START a word  ("lead" -> "leads")
       4+ chars   : whole word within one edit           ("veritaz" -> "veritas")
       6+ chars   : allowed to sit mid-word within one edit ("veritas" -> "digiveritaz")
     Without the length floor on the last tier, "per" would match "expert" and drag half the
     blog into a search for "cost per lead". */
  function near(tok, hay){
    var words = hay.split(/[^a-z0-9']+/), L = tok.length, i, w;
    for (i = 0; i < words.length; i++){
      w = words[i];
      if (!w || w.length > 40) continue;
      if (w.lastIndexOf(tok, 0) === 0) return true;             // prefix of a word
      if (L >= 4 && within1(tok, w)) return true;               // whole word, 1 edit
      if (L >= 6 && w.length > L){                              // inside a longer word, 1 edit
        for (var k = 1; k + L - 1 <= w.length; k++){
          if (within1(tok, w.substr(k, L))) return true;
          if (k + L < w.length && within1(tok, w.substr(k, L + 1))) return true;
        }
      }
    }
    return false;
  }
  /* all=true -> every token must appear (precise); all=false -> any token counts (fallback) */
  function hits(toks, hay, all){
    var h = norm(hay), n = 0;
    for (var i = 0; i < toks.length; i++){
      if (near(toks[i], h)) n++;
      else if (all) return 0;
    }
    return n;
  }

  function scan(toks, all){
    var out = [];
    for (var i = 0; i < idx.p.length; i++){
      var p = idx.p[i], score = 0, matched = [];
      var head = p.ti + ' ' + (p.h1 || '') + ' ' + p.d + ' ' + (p.i || '');
      score += hits(toks, p.ti, all) * 100;
      score += hits(toks, head, all) * 40;
      for (var j = 0; j < p.s.length; j++){
        var sec = p.s[j], n;
        if ((n = hits(toks, sec.h, all))) { matched.push({ h: sec.h, t: sec.t, w: 20 }); score += n * 20; }
        else if ((n = hits(toks, sec.h + ' ' + sec.t, all))) { matched.push({ h: sec.h, t: sec.t, w: 8 }); score += n * 8; }
      }
      if (!score) continue;
      if (p.k === 'Service' || p.k === 'Page') score += 12;   // nudge money pages up
      matched.sort(function(a, b){ return b.w - a.w; });
      out.push({ p: p, score: score, sec: matched.slice(0, MAX_HITS_PER_PAGE) });
    }
    out.sort(function(a, b){ return b.score - a.score || a.p.ti.localeCompare(b.p.ti); });
    return out;
  }

  /* Try the precise all-tokens pass first. If a stray or mistyped word ("bg veritas") would
     otherwise dead-end the query, fall back to any-token so the user still gets somewhere. */
  function search(q){
    var toks = tokens(q);
    if (!toks.length || !idx) return { res: [], loose: false };
    var strict = scan(toks, true);
    if (strict.length || toks.length < 2) return { res: strict, loose: false };
    return { res: scan(toks, false), loose: true };
  }

  /* ---------- rendering ---------- */
  function esc(s){
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  /* Wrap hits in sentinels first, then swap for <mark> — marking directly would let a later
     token match inside the tag text an earlier token just inserted. */
  function mark(text, toks){
    var out = esc(text), i;
    for (i = 0; i < toks.length; i++){
      var t = toks[i].replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      if (t.length < 2) continue;
      out = out.replace(new RegExp('\\b(' + t + ')', 'ig'), '\u0001$1\u0002');
    }
    return out.replace(/\u0001/g, '<mark>').replace(/\u0002/g, '</mark>');
  }
  /* Chrome/Edge scroll straight to the matched text; other browsers just open the page. */
  function hitHref(url, heading){
    try { return url + '#:~:text=' + encodeURIComponent(heading.slice(0, 90)); }
    catch (e) { return url; }
  }

  function render(q){
    var toks = tokens(q);
    if (!toks.length){ panel.innerHTML = ''; setPanel(false); return; }
    if (!idx){
      panel.innerHTML = '<div class="dv-srch-status">' + (loading ? 'Loading…' : 'Search unavailable right now.') + '</div>';
      setPanel(true); return;
    }
    var found = search(q), res = found.res;
    if (!res.length){
      panel.innerHTML = '<div class="dv-srch-status">No matches for “' + esc(q) + '”.</div>';
      setPanel(true); return;
    }
    var total = res.length, html = '', shown = res.slice(0, MAX_PAGES);
    if (found.loose){
      html += '<div class="dv-srch-status">No page matches all of “' + esc(q) + '” — showing the closest results.</div>';
    }
    for (var i = 0; i < shown.length; i++){
      var r = shown[i], p = r.p;
      html += '<div class="dv-srch-group">';
      html += '<div class="dv-srch-page"><span class="dv-srch-kind">' + esc(p.k) + '</span><span>' + mark(p.ti, toks) + '</span></div>';
      html += '<a class="dv-srch-hit" href="' + esc(p.u) + '"><span class="dv-srch-hit-h">' + mark(p.h1 || p.ti, toks) + '</span>'
            + '<span class="dv-srch-hit-t">' + mark((p.d || p.i || '').slice(0, 150), toks) + '</span></a>';
      for (var j = 0; j < r.sec.length; j++){
        var s = r.sec[j];
        html += '<a class="dv-srch-hit" href="' + esc(hitHref(p.u, s.h)) + '">'
              + '<span class="dv-srch-hit-h">' + mark(s.h, toks) + '</span>'
              + (s.t ? '<span class="dv-srch-hit-t">' + mark(s.t, toks) + '</span>' : '') + '</a>';
      }
      html += '</div>';
    }
    if (total > shown.length){
      html += '<span class="dv-srch-more">' + (total - shown.length) + ' more page' + (total - shown.length > 1 ? 's' : '') + ' match — keep typing to narrow</span>';
    }
    panel.innerHTML = html; sel = -1; setPanel(true);
  }

  /* ---------- index ---------- */
  function load(){
    if (idx || loading) return;
    loading = true;
    fetch('/search-index.json', { credentials: 'same-origin' })
      .then(function(r){ if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(j){ idx = j; loading = false; if (input.value.trim()) render(input.value); })
      .catch(function(){ loading = false; if (input.value.trim()) render(input.value); });
  }

  /* ---------- open/close ---------- */
  function setPanel(on){ wrap.classList.toggle('show-panel', !!on); }
  function isMobile(){ return window.matchMedia('(max-width:1050px)').matches; }
  function open(){
    wrap.classList.add('open'); load();
    try { input.focus(); } catch(e){}
    if (input.value.trim()) render(input.value);
  }
  function close(){
    if (isMobile()) { setPanel(false); return; }   // stays expanded inside the mobile menu
    wrap.classList.remove('open'); setPanel(false);
  }

  function items(){ return panel.querySelectorAll('.dv-srch-hit'); }
  function move(d){
    var list = items(); if (!list.length) return;
    if (sel >= 0 && list[sel]) list[sel].classList.remove('sel');
    sel = (sel + d + list.length) % list.length;
    list[sel].classList.add('sel');
    try { list[sel].scrollIntoView({ block: 'nearest' }); } catch(e){}
  }

  function build(){
    var cta = document.querySelector('.nav ul li.cta');
    var ul = document.querySelector('.nav ul');
    if (!ul || document.querySelector('.dv-srch')) return;

    wrap = document.createElement('li');
    wrap.className = 'dv-srch';
    wrap.innerHTML =
      '<div class="dv-srch-box">'
      + '<button type="button" class="dv-srch-btn" aria-label="Search this site" aria-expanded="false">' + ICON + '</button>'
      + '<input type="search" class="dv-srch-input" placeholder="Search services, blogs, case studies…" aria-label="Search this site" autocomplete="off">'
      + '<button type="button" class="dv-srch-clear" aria-label="Clear search">' + XICON + '</button>'
      + '</div>'
      + '<div class="dv-srch-panel" role="listbox" aria-label="Search results"></div>';

    if (cta) ul.insertBefore(wrap, cta); else ul.appendChild(wrap);

    btn = wrap.querySelector('.dv-srch-btn');
    input = wrap.querySelector('.dv-srch-input');
    clear = wrap.querySelector('.dv-srch-clear');
    panel = wrap.querySelector('.dv-srch-panel');

    btn.addEventListener('click', function(e){
      e.preventDefault(); e.stopPropagation();
      if (wrap.classList.contains('open') && !isMobile()){
        if (input.value.trim()){ input.value = ''; wrap.classList.remove('has-q'); setPanel(false); input.focus(); }
        else close();
      } else open();
      btn.setAttribute('aria-expanded', wrap.classList.contains('open') ? 'true' : 'false');
    });

    var timer;
    input.addEventListener('input', function(){
      wrap.classList.toggle('has-q', !!input.value.trim());
      clearTimeout(timer);
      timer = setTimeout(function(){ render(input.value); }, 110);
    });
    input.addEventListener('focus', load);

    clear.addEventListener('click', function(e){
      e.preventDefault(); e.stopPropagation();
      input.value = ''; wrap.classList.remove('has-q'); setPanel(false); input.focus();
    });

    input.addEventListener('keydown', function(e){
      if (e.key === 'Escape'){ input.value=''; wrap.classList.remove('has-q'); close(); input.blur(); }
      else if (e.key === 'ArrowDown'){ e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp'){ e.preventDefault(); move(-1); }
      else if (e.key === 'Enter'){
        var list = items();
        if (sel >= 0 && list[sel]){ e.preventDefault(); location.href = list[sel].getAttribute('href'); }
        else if (list.length){ e.preventDefault(); location.href = list[0].getAttribute('href'); }
      }
    });

    document.addEventListener('click', function(e){
      if (!wrap.contains(e.target)) close();
    });
    /* "/" focuses search, the way most docs sites behave */
    document.addEventListener('keydown', function(e){
      if (e.key === '/' && !/^(input|textarea|select)$/i.test((e.target.tagName || '')) && !e.target.isContentEditable){
        e.preventDefault(); open();
      }
    });
    window.addEventListener('resize', function(){
      if (isMobile()) wrap.classList.add('open');
    });
    if (isMobile()) wrap.classList.add('open');
  }

  if (document.readyState !== 'loading') build();
  else document.addEventListener('DOMContentLoaded', build);
})();

