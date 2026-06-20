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
/* DV-POPUP v1 (abhishek-edits): "Lets Get Project Started" popup (instant) + CTA shine */
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
    var html = ''
      +'<div class="dvm-card" role="document">'
      +'<button class="dvm-close" type="button" aria-label="Close">&times;</button>'
      +'<h2 class="dvm-title">Lets Get Project Started</h2>'
      +'<p class="dvm-sub">Share your goals, budget and timeline &mdash; we&rsquo;ll send a tailored proposal within one business day.</p>'
      +'<form id="dvm-form" class="dvm-form" novalidate>'
      +'<input type="hidden" name="_subject" value="New lead from DigiVeritaz website">'
      +'<input type="hidden" name="_template" value="table">'
      +'<input type="hidden" name="_captcha" value="false">'
      +'<div class="dvm-hp" aria-hidden="true"><label>Leave this empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label><label>Address<input type="text" name="address_line" tabindex="-1" autocomplete="off"></label></div>'
      +'<input type="hidden" name="_ts" id="dvm-ts"><input type="hidden" name="_jsok" id="dvm-jsok">'
      +'<div class="dvm-row">'
      +'<div class="dvm-field"><label>Full Name <span class="req">*</span></label><input type="text" name="fullname" placeholder="Your full name" required></div>'
      +'<div class="dvm-field"><label>Email Address <span class="req">*</span></label><input type="email" name="email" placeholder="you@company.com" required></div>'
      +'<div class="dvm-field"><label>Phone Number <span class="req">*</span></label><input type="tel" name="phone" placeholder="+91 9XXXXXXXXX" required></div>'
      +'</div>'
      +'<div class="dvm-row">'
      +'<div class="dvm-field"><label>Company Name</label><input type="text" name="company" placeholder="Company"></div>'
      +'<div class="dvm-field col2"><label>Budget Range <span class="req">*</span></label><select name="budget" required><option value="">-- Please select budget range --</option><option>INR 40k &ndash; 60k</option><option>INR 60k to 1 Lac</option><option>INR 1 Lac and above</option></select></div>'
      +'</div>'
      +'<div class="dvm-seclabel">Select the Services You Need</div>'
      +'<div class="dvm-checks">'+checks+'</div>'
      +'<div class="dvm-field full" style="margin-bottom:14px"><label>Project Brief</label><textarea name="message" rows="2" placeholder="Tentative start date, goals, platforms of interest&hellip;"></textarea></div>'
      +'<button class="dvm-send" type="button" id="dvm-getotp">Send verification code</button>'
      +'<div id="dvm-otpwrap" style="display:none;margin-top:12px">'
      +'<div class="dvm-field full"><label>Enter the 6-digit code emailed to you <span class="req">*</span></label><input type="text" id="dvm-otp" inputmode="numeric" maxlength="6" placeholder="123456" style="letter-spacing:.35em;text-align:center;font-size:1.15rem"></div>'
      +'<button class="dvm-send" type="submit" style="margin-top:10px">Verify &amp; Send</button>'
      +'<div style="text-align:center;margin-top:8px"><a href="#" id="dvm-resend" style="font-size:.82rem;color:#16a34a;text-decoration:underline">Resend code</a></div>'
      +'</div>'
      +'<div class="dvm-msg" id="dvm-msg"></div>'
      +'</form>'
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
    document.getElementById('dvm-getotp').addEventListener('click', function(){ requestOtp(false); });
    document.getElementById('dvm-resend').addEventListener('click', function(e){ e.preventDefault(); requestOtp(true); });
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

  function collect(form){
    var fd = new FormData(form), data = {};
    fd.forEach(function(v,k){
      if (data[k] !== undefined){ if (!Array.isArray(data[k])) data[k] = [data[k]]; data[k].push(v); }
      else data[k] = v;
    });
    return data;
  }
  function postForm(payload, cb){
    var body = new URLSearchParams();
    Object.keys(payload).forEach(function(k){
      var v = payload[k];
      if (Array.isArray(v)) v.forEach(function(x){ body.append(k, x); });
      else if (v != null) body.append(k, String(v));
    });
    fetch(ENDPOINT, { method:'POST', body: body })
      .then(function(r){ return r.json().catch(function(){ return { ok:false, error:'bad_response' }; }); })
      .then(cb).catch(function(){ cb({ ok:false, error:'network' }); });
  }
  function dmsg(t,c){ var m = document.getElementById('dvm-msg'); if (m){ m.textContent = t; m.style.color = c || '#374151'; } }
  function requestOtp(resend){
    var form = document.getElementById('dvm-form'); var data = collect(form);
    if (!data.fullname || !data.email || !data.phone){ dmsg('Please fill in your name, email and phone first.', '#dc2626'); return; }
    if (!data.budget){ dmsg('Please select a budget range.', '#dc2626'); return; }
    var b = document.getElementById('dvm-getotp'); if (b) b.disabled = true;
    dmsg(resend ? 'Sending a new code…' : 'Sending verification code…');
    var payload = Object.assign({}, data, { action:'request_otp' }); delete payload.otp;
    postForm(payload, function(res){
      if (b) b.disabled = false;
      if (res && res.ok){
        document.getElementById('dvm-otpwrap').style.display = 'block';
        if (b) b.style.display = 'none';
        dmsg('Code sent! Check your inbox (and spam).', '#16a34a');
        var o = document.getElementById('dvm-otp'); if (o) o.focus();
      } else {
        dmsg('Could not send code' + (res && res.error ? ': ' + res.error : '') + '. Please WhatsApp +91 99566 55662.', '#dc2626');
      }
    });
  }
  function onSubmit(ev){
    ev.preventDefault();
    var form = ev.target, data = collect(form);
    var otp = (document.getElementById('dvm-otp') || {}).value || '';
    if (!/^[0-9]{6}$/.test(otp)){ dmsg('Enter the 6-digit code from your email.', '#dc2626'); return; }
    var vbtn = form.querySelector('#dvm-otpwrap .dvm-send'); if (vbtn) vbtn.disabled = true;
    dmsg('Verifying…');
    var payload = Object.assign({}, data, { action:'submit_form', otp: otp });
    postForm(payload, function(res){
      if (res && res.ok){
        var card = document.querySelector('#dvm-overlay .dvm-card');
        if (card){
          card.innerHTML = '<button class="dvm-close" type="button" aria-label="Close">&times;</button>'
            + '<div class="dvm-thanks"><h3>Thank you for filling the form</h3><p>Your email is verified and your details are on their way — we&rsquo;ll get back within one business day.</p></div>';
          card.querySelector('.dvm-close').addEventListener('click', closeModal);
        }
      } else {
        if (vbtn) vbtn.disabled = false;
        dmsg('Verification failed' + (res && res.error ? ': ' + res.error : '') + '. Re-check the code or WhatsApp +91 99566 55662.', '#dc2626');
      }
    });
  }

  function wire(){
    var nodes = document.querySelectorAll('a.btn, button.btn');
    Array.prototype.forEach.call(nodes, function(el){
      var t = (el.textContent || '').trim().toLowerCase();
      var book = (t === 'book a call');
      var prop = /free proposal/.test(t);
      if (book || prop) el.classList.add('dv-shine');
      if (book){
        el.addEventListener('click', function(e){ e.preventDefault(); openModal(); });
      }
    });
  }
  window.dvOpenModal = openModal; function dvReady(){ wire(); setTimeout(function(){ openModal(); }, 3000); } if (document.readyState !== 'loading') dvReady();
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
      toast('Live chat is coming soon!');
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
    fetch("/api/chat", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ page: location.pathname, messages: msgs })
    }).then(function(r){ return r.json(); }).then(function(d){
      typing(false);
      var rep = (d && d.reply) || "Sorry, please try again.";
      var svcs = (d && d.services) || [];
      msgs.push({ role: "assistant", content: rep, services: svcs }); addMsg("assistant", rep, svcs); save();
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

  if (document.readyState !== "loading") build();
  else document.addEventListener("DOMContentLoaded", build);
})();
