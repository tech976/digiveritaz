/* DigiVeritaz AI News — subscribe flow (details -> email OTP -> subscribed)
 *
 * Backend: two same-origin Vercel functions in this repo.
 *   POST /api/otp-send    {name,email}     -> {ok, token}   mails a 6-digit code
 *   POST /api/otp-verify  {token,code}     -> {ok}          verifies, subscribes,
 *                                                           sends the welcome email
 *
 * Email is sent with Resend from those functions, never from here: the Resend API
 * key is a secret (a leaked one lets anyone send mail as digiveritaz.com), Resend
 * refuses browser origins outright, and a code the browser generates or holds is
 * trivially read from devtools — which would defeat the whole point of verifying.
 *
 * The address is carried inside the SIGNED token, so it cannot be swapped between
 * the two steps. The plaintext code never comes back to the browser.
 */
(function () {
  'use strict';
  if (window.__dvAiNews) return;
  window.__dvAiNews = true;

  var API_SEND = '/api/otp-send';
  var API_VERIFY = '/api/otp-verify';

  /* Local review mode. `python -m http.server` cannot run the Vercel functions, so
     on localhost we simulate the round-trip instead of failing. Never active on the
     real site (hostname check, not a build flag). */
  var MOCK = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || location.protocol === 'file:';
  var MOCK_CODE = '123456';

  var $ = function (id) { return document.getElementById(id); };

  var ov = $('ain-ov');
  if (!ov) return;
  var s1 = $('ain-s1'), s2 = $('ain-s2'), s3 = $('ain-s3');
  var e1 = $('ain-e1'), e2 = $('ain-e2');
  var b1 = $('ain-b1'), b2 = $('ain-b2');
  var mock = $('ain-mock');
  var otpInputs = s2.querySelectorAll('.ain-otp input');
  var steps = ov.querySelectorAll('.ain-steps span');
  var state = { name: '', email: '', token: '', tick: null };

  /* ---------- helpers ---------- */
  function showErr(el, msg) { el.textContent = msg; el.classList.add('show'); }
  function clearErr(el) { el.textContent = ''; el.classList.remove('show'); }
  function busy(btn, on, label) {
    btn.disabled = on;
    if (on) { btn.dataset.label = btn.textContent; btn.textContent = label; }
    else if (btn.dataset.label) { btn.textContent = btn.dataset.label; }
  }
  function setStep(n) {
    for (var i = 0; i < steps.length; i++) steps[i].classList.toggle('on', i < n);
    s1.style.display = n === 1 ? '' : 'none';
    s2.style.display = n === 2 ? '' : 'none';
    s3.style.display = n === 3 ? '' : 'none';
  }
  function validEmail(v) { return /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(v); }

  function post(url, payload) {
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (r) { return r.json().catch(function () { return { ok: false, error: 'server' }; }); })
      .catch(function () { return { ok: false, error: 'network' }; });
  }

  var ERRORS = {
    bad_email: 'That email address does not look right. Please check and try again.',
    otp_rate_limited: 'Too many codes requested. Please wait an hour and try again.',
    mail_failed: 'We could not send the email just now. Please try again in a minute.',
    otp_invalid: 'That code is not correct. Please check and try again.',
    otp_expired: 'That code has expired. Request a new one.',
    subscribe_failed: 'We could not complete your subscription. Please try again shortly.',
    server: 'Something went wrong at our end. Please try again.',
    network: 'Network problem. Please check your connection and try again.'
  };
  function msgFor(err) { return ERRORS[err] || 'Something went wrong. Please try again.'; }

  /* ---------- open / close ---------- */
  function open() {
    setStep(1);
    clearErr(e1); clearErr(e2);
    ov.classList.add('is-open');
    ov.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    if (MOCK) {
      mock.innerHTML = '<strong>Local review mode.</strong> No email is sent and nothing is ' +
                       'subscribed. Use code <strong>' + MOCK_CODE + '</strong> at the verify step.';
      mock.classList.add('show');
    }
    var n = $('ain-name'); if (n) { try { n.focus(); } catch (e) {} }
  }
  function close() {
    ov.classList.remove('is-open');
    ov.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (state.tick) { clearInterval(state.tick); state.tick = null; }
  }
  document.addEventListener('click', function (ev) {
    var o = ev.target.closest ? ev.target.closest('[data-ain-open]') : null;
    if (o) { ev.preventDefault(); open(); return; }
    var c = ev.target.closest ? ev.target.closest('[data-ain-close]') : null;
    if (c) { ev.preventDefault(); close(); return; }
    if (ev.target === ov) close();
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && ov.classList.contains('is-open')) close();
  });

  /* ---------- step 1: request the code ---------- */
  s1.addEventListener('submit', function (ev) {
    ev.preventDefault();
    clearErr(e1);
    var name = $('ain-name').value.trim();
    var email = $('ain-email').value.trim();
    var hp = s1.querySelector('input[name=_hp_site]');

    if (hp && hp.value) { setStep(3); return; }            // bot: pretend it worked
    if (!name) { showErr(e1, 'Please enter your name.'); return; }
    if (!validEmail(email)) { showErr(e1, 'Please enter a valid email address.'); return; }

    state.name = name; state.email = email;
    busy(b1, true, 'Sending code…');

    var req = MOCK
      ? Promise.resolve({ ok: true, token: 'mock' })
      : post(API_SEND, { name: name, email: email, hp: hp ? hp.value : '' });

    req.then(function (res) {
      busy(b1, false);
      if (!res || !res.ok) { showErr(e1, msgFor(res && res.error)); return; }
      state.token = res.token;
      $('ain-to').textContent = email;
      setStep(2);
      otpInputs[0].focus();
      startResendTimer();
    });
  });

  /* ---------- OTP box behaviour ---------- */
  function otpValue() {
    var v = '';
    for (var i = 0; i < otpInputs.length; i++) v += otpInputs[i].value;
    return v;
  }
  for (var i = 0; i < otpInputs.length; i++) {
    (function (idx) {
      var el = otpInputs[idx];
      el.addEventListener('input', function () {
        el.value = el.value.replace(/\D/g, '').slice(0, 1);
        if (el.value && idx < otpInputs.length - 1) otpInputs[idx + 1].focus();
        if (otpValue().length === 6) clearErr(e2);
      });
      el.addEventListener('keydown', function (ev) {
        if (ev.key === 'Backspace' && !el.value && idx > 0) otpInputs[idx - 1].focus();
      });
      el.addEventListener('paste', function (ev) {
        var t = (ev.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
        if (!t) return;
        ev.preventDefault();
        for (var j = 0; j < otpInputs.length; j++) otpInputs[j].value = t.charAt(j) || '';
        otpInputs[Math.min(t.length, otpInputs.length) - 1].focus();
      });
    })(i);
  }

  /* ---------- step 2: verify + subscribe ---------- */
  s2.addEventListener('submit', function (ev) {
    ev.preventDefault();
    clearErr(e2);
    var code = otpValue();
    if (code.length !== 6) { showErr(e2, 'Please enter all six digits.'); return; }

    busy(b2, true, 'Verifying…');

    var req = MOCK
      ? Promise.resolve(code === MOCK_CODE ? { ok: true } : { ok: false, error: 'otp_invalid' })
      : post(API_VERIFY, { token: state.token, code: code });

    req.then(function (res) {
      busy(b2, false);
      if (!res || !res.ok) {
        showErr(e2, msgFor(res && res.error));
        for (var j = 0; j < otpInputs.length; j++) otpInputs[j].value = '';
        otpInputs[0].focus();
        return;
      }
      if (state.tick) { clearInterval(state.tick); state.tick = null; }
      setStep(3);
      try {
        if (window.dataLayer) window.dataLayer.push({ event: 'ai_news_subscribe' });
        if (window.gtag) window.gtag('event', 'ai_news_subscribe', { method: 'email_otp' });
      } catch (e) {}
    });
  });

  /* ---------- resend ---------- */
  function startResendTimer() {
    var left = 30, btn = $('ain-resend'), lbl = $('ain-timer');
    btn.disabled = true;
    lbl.textContent = 'in ' + left + 's';
    if (state.tick) clearInterval(state.tick);
    state.tick = setInterval(function () {
      left -= 1;
      if (left <= 0) {
        clearInterval(state.tick); state.tick = null;
        btn.disabled = false; lbl.textContent = '';
      } else {
        lbl.textContent = 'in ' + left + 's';
      }
    }, 1000);
  }
  $('ain-resend').addEventListener('click', function () {
    clearErr(e2);
    var btn = $('ain-resend');
    btn.disabled = true;
    var req = MOCK ? Promise.resolve({ ok: true, token: 'mock' })
                   : post(API_SEND, { name: state.name, email: state.email });
    req.then(function (res) {
      if (!res || !res.ok) { showErr(e2, msgFor(res && res.error)); btn.disabled = false; return; }
      state.token = res.token;      // the old token is now stale
      startResendTimer();
    });
  });

  /* ---------- FAQ accordion (page-local) ---------- */
  var qs = document.querySelectorAll('.ain-faq-q');
  for (var q = 0; q < qs.length; q++) {
    qs[q].addEventListener('click', function () {
      this.parentNode.classList.toggle('open');
    });
  }
})();
