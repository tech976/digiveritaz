// DigiVeritaz static site — minimal JS
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
  var themeBtn = document.querySelector('.theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      if (next === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
      else document.documentElement.removeAttribute('data-theme');
      try { localStorage.setItem('dv-theme', next); } catch (e) {}
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
            // Restore scroll on next frame in case anything tried to shift it
            requestAnimationFrame(function () { navList.scrollTop = prevScroll; });
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
      'https://script.google.com/macros/s/AKfycbz5_zT_5sycLdaSgIbEsNy2W8kNPxozOlcjBnNvu4SOhECw4lzIpCgjsmVIiHo5G0Lw/exec';

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
        window.location.href = 'thank-you.html';
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
            window.location.href = 'thank-you.html';
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

/* DV-POPUP v1 (abhishek-edits): "Lets Get Project Started" popup + CTA shine */
;(function(){
  if (window.__dvmInit) return; window.__dvmInit = true;
  var ENDPOINT = 'https://script.google.com/macros/s/AKfycbz5_zT_5sycLdaSgIbEsNy2W8kNPxozOlcjBnNvu4SOhECw4lzIpCgjsmVIiHo5G0Lw/exec';
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
  function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

  function buildModal(){
    if (document.getElementById('dvm-overlay')) return;
    var checks = SERVICES.map(function(s){
      return '<label><input type="checkbox" name="services[]" value="'+esc(s[0])+'">'+esc(s[1])+'</label>';
    }).join('');
    var art = '<div class="dvm-art" aria-hidden="true"><svg viewBox="0 0 240 150" width="100%" fill="none">'
      +'<rect x="10" y="14" width="220" height="122" rx="12" fill="rgba(255,255,255,.10)" stroke="rgba(255,255,255,.5)"/>'
      +'<circle cx="26" cy="30" r="3.5" fill="#fff"/><circle cx="38" cy="30" r="3.5" fill="rgba(255,255,255,.6)"/><circle cx="50" cy="30" r="3.5" fill="rgba(255,255,255,.4)"/>'
      +'<rect x="26" y="52" width="120" height="9" rx="4.5" fill="rgba(255,255,255,.65)"/>'
      +'<rect x="26" y="70" width="150" height="9" rx="4.5" fill="rgba(255,255,255,.4)"/>'
      +'<rect x="26" y="88" width="92" height="9" rx="4.5" fill="rgba(255,255,255,.4)"/>'
      +'<circle cx="192" cy="92" r="22" fill="rgba(255,255,255,.18)" stroke="#fff" stroke-width="2"/>'
      +'<path d="M182 92l7 7 13-15" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
      +'</svg></div>';
    var html = ''
      +'<div class="dvm-card" role="document">'
      +'<button class="dvm-close" type="button" aria-label="Close">&times;</button>'
      +'<div class="dvm-form-col">'
      +'<h2 class="dvm-title">Lets Get Project Started</h2>'
      +'<p class="dvm-sub">Share your goals, budget and timeline &mdash; we&rsquo;ll send a tailored proposal within one business day.</p>'
      +'<form id="dvm-form" novalidate>'
      +'<input type="hidden" name="_subject" value="New lead from DigiVeritaz website">'
      +'<input type="hidden" name="_template" value="table">'
      +'<input type="hidden" name="_captcha" value="false">'
      +'<div class="dvm-hp" aria-hidden="true"><label>Leave this empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label><label>Address<input type="text" name="address_line" tabindex="-1" autocomplete="off"></label></div>'
      +'<input type="hidden" name="_ts" id="dvm-ts"><input type="hidden" name="_jsok" id="dvm-jsok">'
      +'<div class="dvm-two"><div class="dvm-field"><label>Full Name <span class="req">*</span></label><input type="text" name="fullname" placeholder="Your full name" required></div><div class="dvm-field"><label>Email Address <span class="req">*</span></label><input type="email" name="email" placeholder="you@company.com" required></div></div>'
      +'<div class="dvm-two"><div class="dvm-field"><label>Phone Number <span class="req">*</span></label><input type="tel" name="phone" placeholder="+91 9XXXXXXXXX" required></div><div class="dvm-field"><label>Company Name</label><input type="text" name="company" placeholder="Company"></div></div>'
      +'<div class="dvm-field"><label>Budget Range <span class="req">*</span></label><select name="budget" required><option value="">-- Please select budget range --</option><option>INR 40k &ndash; 60k</option><option>INR 60k to 1 Lac</option><option>INR 1 Lac and above</option></select></div>'
      +'<div class="dvm-seclabel">Select the Services You Need</div>'
      +'<div class="dvm-checks">'+checks+'</div>'
      +'<div class="dvm-field"><label>Project Brief</label><textarea name="message" rows="4" placeholder="Tentative start date, goals, platforms of interest, reference brands&hellip;"></textarea></div>'
      +'<button class="dvm-send" type="submit">Send</button>'
      +'<div class="dvm-msg" id="dvm-msg"></div>'
      +'</form>'
      +'</div>'
      +'<div class="dvm-visual-col" aria-hidden="true">'
      +'<h3>Let&rsquo;s build something that grows your business.</h3>'
      +'<p>Tell us where you want to go &mdash; we&rsquo;ll map the fastest route there.</p>'
      +'<ul>'
      +'<li><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Free, tailored proposal in 1 business day</li>'
      +'<li><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Trusted by 600+ brands across India, UAE &amp; UK</li>'
      +'<li><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Performance-driven, ROI-first strategy</li>'
      +'</ul>'
      + art
      +'</div>';
    var ov = document.createElement('div');
    ov.className = 'dvm-overlay'; ov.id = 'dvm-overlay';
    ov.setAttribute('role','dialog'); ov.setAttribute('aria-modal','true');
    ov.setAttribute('aria-label','Start your project'); ov.setAttribute('aria-hidden','true');
    ov.innerHTML = html;
    document.body.appendChild(ov);
    ov.querySelector('.dvm-close').addEventListener('click', closeModal);
    ov.addEventListener('mousedown', function(e){ if (e.target === ov) closeModal(); });
    document.getElementById('dvm-form').addEventListener('submit', onSubmit);
  }

  function openModal(){
    buildModal();
    var ov = document.getElementById('dvm-overlay'); if (!ov) return;
    var ts = document.getElementById('dvm-ts'), js = document.getElementById('dvm-jsok');
    if (ts) ts.value = String(Date.now());
    if (js) js.value = 'dv-' + Math.random().toString(36).slice(2, 12);
    ov.classList.add('is-open'); ov.setAttribute('aria-hidden','false');
    document.body.classList.add('dvm-lock');
    var f = ov.querySelector('input[name=fullname]'); if (f) { try { f.focus(); } catch(e){} }
  }
  function closeModal(){
    var ov = document.getElementById('dvm-overlay'); if (!ov) return;
    ov.classList.remove('is-open'); ov.setAttribute('aria-hidden','true');
    document.body.classList.remove('dvm-lock');
  }
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') closeModal(); });

  function onSubmit(ev){
    ev.preventDefault();
    var form = ev.target, msg = document.getElementById('dvm-msg'), btn = form.querySelector('.dvm-send');
    function show(t,c){ if (msg){ msg.textContent = t; msg.style.color = c || '#374151'; } }
    var fd = new FormData(form), data = {};
    fd.forEach(function(v,k){
      if (data[k] !== undefined){ if (!Array.isArray(data[k])) data[k] = [data[k]]; data[k].push(v); }
      else data[k] = v;
    });
    if (!data.fullname || !data.email || !data.phone){ show('Please fill in your name, email and phone.', '#dc2626'); return; }
    if (!data.budget){ show('Please select a budget range.', '#dc2626'); return; }
    btn.disabled = true; show('Sending…');
    var body = new URLSearchParams();
    Object.keys(data).forEach(function(k){
      var v = data[k];
      if (Array.isArray(v)) v.forEach(function(x){ body.append(k, x); });
      else if (v != null) body.append(k, String(v));
    });
    body.append('action','submit_form');
    fetch(ENDPOINT, { method:'POST', body: body })
      .then(function(r){ return r.json().catch(function(){ return { ok:false }; }); })
      .then(function(res){
        if (res && res.ok){
          form.innerHTML = '<div style="text-align:center;padding:40px 10px"><h3 style="color:#16a34a;margin:0 0 12px">Thank you!</h3><p style="color:#475569">Your message is on its way. We&rsquo;ll get back within one business day.</p></div>';
        } else {
          btn.disabled = false;
          show('Submission failed' + (res && res.error ? ': ' + res.error : '') + '. Please try the contact page.', '#dc2626');
        }
      })
      .catch(function(){ btn.disabled = false; show('Network error. Please try again or use the contact page.', '#dc2626'); });
  }

  function spinner(on){
    var s = document.getElementById('dvm-spinner');
    if (on){ if (!s){ s = document.createElement('div'); s.id = 'dvm-spinner'; s.className = 'dvm-spinner'; document.body.appendChild(s); } }
    else if (s){ s.parentNode.removeChild(s); }
  }

  function wire(){
    var nodes = document.querySelectorAll('a.btn, button.btn');
    Array.prototype.forEach.call(nodes, function(el){
      var t = (el.textContent || '').trim().toLowerCase();
      var book = (t === 'book a call');
      var prop = /free proposal/.test(t);
      if (book || prop) el.classList.add('dv-shine');
      if (book){
        el.addEventListener('click', function(e){
          e.preventDefault();
          spinner(true);
          setTimeout(function(){ spinner(false); openModal(); }, 2000);
        });
      }
    });
  }
  if (document.readyState !== 'loading') wire();
  else document.addEventListener('DOMContentLoaded', wire);
})();

