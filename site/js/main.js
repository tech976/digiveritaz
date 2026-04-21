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

  // Mobile nav toggle
  var hamb = document.querySelector('.hamb');
  var menu = document.querySelector('.nav ul');
  if (hamb && menu) {
    hamb.addEventListener('click', function () { menu.classList.toggle('open'); });
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
          document.querySelectorAll('.has-dd.open').forEach(function (el) {
            if (el !== parent) el.classList.remove('open');
          });
          parent.classList.add('open');
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

  // Contact form — validates, submits to FormSubmit.co (AJAX), falls back to mailto
  var form = document.getElementById('contact-form');
  if (form) {
    var CONTACT_EMAIL = 'poojanvig.pv@gmail.com';

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

      var data = new FormData(form);
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
  }
});
