/* DV-LEAD v2 — full-screen 3-step progressive lead form for DigiVeritaz.
   Two render modes from ONE codebase:
     • Overlay popup  — opens from CTAs (full-page takeover, logo + close).
     • Inline page    — if a #dvl-inline container exists, the form renders into it
                        (used by the standalone /get-proposal/ page).
   Flow: Step1 service+phone+consent -> Proceed (number saved instantly) + SMS OTP;
   Step2 name+email; Step3 company/website+message -> Submit (full lead).
   Abandon after step 1 = the number is already a Partial lead.
   This is the CTA popup: every CTA opens it. It is loaded on every page by main.js
   and coexists with the wide auto-open popup (it no longer disables it).
   Not connected to the contact-us page. */
;(function(){
  if (window.__dvLeadV2) return; window.__dvLeadV2 = true;
  /* This is the CTA popup ("Get Your Free Proposal"). It coexists with the wide
     auto-open popup in main.js, so it must NOT disable that one. */

  var ENDPOINT = 'https://script.google.com/macros/s/AKfycby3DZjNUqSEU2Pg2rv45pnYTZT78L4405Et0SJ_NOBybsDLyd6ZWzxlSaEMx1TnKZkc/exec';
  var DVL_LOAD = Date.now();
  /* same 12 services as the wide popup so both write identical Sheet columns ([value, label]) */
  var SERVICES = [['Organic Marketing','Organic Marketing'],['Paid Social Media','Paid Social Media Advertising'],['PPC','Pay-Per-Click Advertising'],['Performance Marketing','Performance Marketing'],['E-commerce','E-commerce Platforms'],['Data Strategy','Data Strategy & Consulting'],['Native Advertising','Native Advertising'],['WhatsApp','WhatsApp Marketing'],['Branding','Branding & Design'],['SEO','Search Engine Optimization'],['GSO','Generative Search Optimisation'],['Tech & Development','Tech & Development']];

  var leadId = '', jsok = '', state = {}, savedOnce = false, completed = false, step = 1, inline = false, formStart = 0;

  /* Every completed submission redirects here so the conversion fires on a real,
     trackable URL (GTM/GA4) instead of an in-place "thank you" screen. */
  var THANKYOU_URL = '/thank-you/';

  function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function $(s,c){ return (c||document).querySelector(s); }

  var WA_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.5 3.5A11.4 11.4 0 0 0 12 0C5.5 0 .2 5.3.2 11.8c0 2.1.5 4.1 1.6 5.9L0 24l6.4-1.7c1.7.9 3.6 1.4 5.6 1.4 6.5 0 11.8-5.3 11.8-11.8 0-3.2-1.2-6.1-3.3-8.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4a9.7 9.7 0 0 1-1.5-5.4C2.2 6.4 6.6 2 12 2s9.8 4.4 9.8 9.8-4.4 10-9.8 10z"/></svg>';
  var BRAND = '<a class="dvl-brand" href="/" aria-label="DigiVeritaz home"><img src="/assets/logo.webp?v=3" alt="DigiVeritaz" width="34" height="34" decoding="async"><span>DigiVeritaz</span></a>';

  /* ---------- styles (self-contained) ---------- */
  function injectCSS(){
    if (document.getElementById('dvl-css')) return;
    var css = ''
    + '.dvl-overlay{position:fixed;inset:0;z-index:2147483600;background:#fff;opacity:0;visibility:hidden;overflow:hidden;transition:opacity .3s ease,visibility .3s}'
    + '.dvl-overlay.is-open{opacity:1;visibility:visible}'
    + '.dvl-overlay .dvl-shell{transform:translateY(18px);transition:transform .36s cubic-bezier(.2,.7,.3,1)}'
    + '.dvl-overlay.is-open .dvl-shell{transform:none}'
    + '.dvl-shell,.dvl-page{display:flex;flex-direction:column;height:100%;min-height:100%;background:#fff;font-family:"Inter Tight",Inter,system-ui,sans-serif}'
    + '.dvl-page{min-height:100vh}'
    + '.dvl-topbar{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;padding:14px 18px;box-shadow:0 1px 0 rgba(2,6,23,.06),0 8px 18px -12px rgba(2,6,23,.22)}'
    + '.dvl-brand{display:flex;align-items:center;gap:9px;text-decoration:none}'
    + '.dvl-brand img{width:34px;height:34px;object-fit:contain;flex:0 0 auto}'
    + '.dvl-brand span{font-weight:800;font-size:1.32rem;color:#0b1220;letter-spacing:-.02em}'
    + '.dvl-close{width:42px;height:42px;border:0;background:transparent;color:#0f172a;font-size:26px;line-height:1;cursor:pointer;border-radius:999px;transition:background .2s;-webkit-tap-highlight-color:transparent}'
    + '.dvl-close:hover{background:#f1f5f9}'
    + '.dvl-body{flex:1 1 auto;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;display:flex;justify-content:center;padding:34px 20px 48px}'
    + '.dvl-inner{width:100%;max-width:460px}'
    + '.dvl-title{margin:4px 0 6px;text-align:center;color:#0f2a5a;font-weight:800;font-size:1.6rem;letter-spacing:-.01em}'
    + '.dvl-sub{margin:0 0 20px;text-align:center;color:#64748b;font-size:.92rem;line-height:1.5}'
    + '.dvl-steps{display:flex;gap:6px;justify-content:center;margin:0 0 22px}'
    + '.dvl-steps i{width:34px;height:5px;border-radius:999px;background:#e2e8f0;transition:background .3s}'
    + '.dvl-steps i.on{background:linear-gradient(135deg,#22c55e,#16a34a)}'
    + '.dvl-step{display:none;animation:dvlFade .3s ease}.dvl-step.is-active{display:block}'
    + '@keyframes dvlFade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}'
    + '.dvl-f{margin:0 0 14px}'
    + '.dvl-f label{display:block;font-size:.8rem;font-weight:700;color:#334155;margin:0 0 6px}'
    + '.dvl-f input,.dvl-f select,.dvl-f textarea{width:100%;box-sizing:border-box;padding:15px 16px;border:1.5px solid #e5e7eb;border-radius:14px;font-size:1rem;font-family:inherit;color:#0f172a;background:#fff;outline:none;transition:border-color .2s,box-shadow .2s}'
    + '.dvl-f textarea{resize:vertical;min-height:88px}'
    + '.dvl-f input:focus,.dvl-f select:focus,.dvl-f textarea:focus{border-color:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.15)}'
    + '.dvl-phone{display:flex;gap:8px}'
    + '.dvl-cc{display:flex;align-items:center;gap:6px;flex:0 0 auto;padding:0 15px;border:1.5px solid #e5e7eb;border-radius:14px;background:#f8fafc;font-weight:700;color:#0f172a;font-size:1.05rem;white-space:nowrap}'
    + '.dvl-phone input{flex:1 1 auto}'
    + '.dvl-note{margin:-4px 0 16px;text-align:center;color:#64748b;font-size:.85rem;display:flex;align-items:center;justify-content:center;gap:6px}'
    + '.dvl-note svg{width:16px;height:16px;color:#22c55e}'
    + '.dvl-consent{display:flex;gap:10px;align-items:flex-start;margin:8px 0 20px;font-size:.82rem;color:#475569;line-height:1.5}'
    + '.dvl-consent input{flex:0 0 auto;width:19px;height:19px;margin-top:1px;accent-color:#2563eb;cursor:pointer}'
    + '.dvl-consent a{color:#2563eb;text-decoration:none}'
    + '.dvl-btn{width:100%;border:0;border-radius:15px;padding:16px 18px;font-family:inherit;font-weight:800;font-size:1.05rem;color:#04240f;background:linear-gradient(135deg,#22c55e,#16a34a);cursor:pointer;position:relative;overflow:hidden;box-shadow:0 14px 30px rgba(22,163,74,.3);transition:transform .15s,box-shadow .2s,opacity .2s;-webkit-tap-highlight-color:transparent}'
    + '.dvl-btn:hover{transform:translateY(-1px)}.dvl-btn:active{transform:translateY(0)}'
    + '.dvl-btn[disabled]{background:#e2e8f0;color:#94a3b8;box-shadow:none;cursor:not-allowed;transform:none}'
    + '.dvl-btn:not([disabled])::after{content:"";position:absolute;top:0;bottom:0;left:-160%;width:55%;background:linear-gradient(120deg,transparent,rgba(255,255,255,.5),transparent);transform:skewX(-20deg);animation:dvlShine 3s ease-in-out infinite;pointer-events:none}'
    + '@keyframes dvlShine{0%{left:-160%}60%,100%{left:170%}}'
    + '.dvl-actions{display:flex;gap:10px;align-items:center}'
    + '.dvl-back{flex:0 0 auto;border:1.5px solid #e5e7eb;background:#fff;color:#475569;border-radius:15px;padding:16px 20px;font-family:inherit;font-weight:700;font-size:1rem;cursor:pointer}'
    + '.dvl-back:hover{background:#f8fafc}'
    + '.dvl-actions .dvl-btn{flex:1 1 auto}'
    + '.dvl-err{color:#dc2626;font-size:.85rem;margin:12px 2px 0;min-height:1em;text-align:center}'
    + '.dvl-thanks{text-align:center;padding:30px 4px 6px}'
    + '.dvl-thanks .tick{width:66px;height:66px;border-radius:999px;margin:0 auto 16px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff}'
    + '.dvl-thanks .tick svg{width:32px;height:32px}'
    + '.dvl-thanks h3{margin:0 0 8px;color:#0f2a5a;font-size:1.5rem;font-weight:800}'
    + '.dvl-thanks p{margin:0;color:#64748b;font-size:.95rem;line-height:1.6}'
    + '.dvl-otpinfo{margin:0 0 16px;text-align:center;color:#475569;font-size:.95rem;line-height:1.5}'
    + '.dvl-otpinfo strong{color:#0f172a;white-space:nowrap}'
    + '#dvl-otp{text-align:center;letter-spacing:.45em;font-weight:800;font-size:1.25rem}'
    + '.dvl-resendrow{margin-top:16px;text-align:center;color:#64748b;font-size:.86rem}'
    + '.dvl-resendrow a{color:#16a34a;font-weight:700;text-decoration:none}'
    + '.dvl-checks{display:grid;grid-template-columns:1fr 1fr;gap:9px 12px;margin-top:4px}'
    + '.dvl-chk{display:flex;align-items:center;gap:8px;font-size:.85rem;color:#334155;font-weight:500;cursor:pointer;line-height:1.3}'
    + '.dvl-chk input{width:17px;height:17px;accent-color:#16a34a;cursor:pointer;flex:0 0 auto}'
    + 'body.dvl-lock{overflow:hidden}'
    + 'body.dvl-lock .dv-mbar,body.dvl-lock .dv-wafloat,body.dvl-lock .dv-topbar,body.dvl-lock .to-top{display:none !important}'
    + '@media (max-width:480px){.dvl-title{font-size:1.42rem}.dvl-body{padding:28px 18px 44px}}';
    var st = document.createElement('style'); st.id = 'dvl-css'; st.textContent = css; document.head.appendChild(st);
  }

  /* ---------- shared form markup + wiring ---------- */
  function formInner(){
    var opts = '<option value="">Service interested in…</option>' + SERVICES.map(function(s){ return '<option value="'+esc(s[0])+'">'+esc(s[1])+'</option>'; }).join('');
    var checks = SERVICES.map(function(s){ return '<label class="dvl-chk"><input type="checkbox" name="services[]" value="'+esc(s[0])+'">'+esc(s[1])+'</label>'; }).join('');
    return ''
    + '<h2 class="dvl-title">Get Your Free Proposal</h2>'
    + '<p class="dvl-sub">Tell us where you want to grow — we’ll send a tailored plan within one business day.</p>'
    + '<div class="dvl-steps"><i class="on"></i><i></i><i></i></div>'
    + '<form class="dvl-form" novalidate autocomplete="on">'
    + '<div style="position:absolute;left:-9999px" aria-hidden="true"><input type="text" name="_honey" tabindex="-1" autocomplete="off"></div>'
    + '<div class="dvl-step is-active" data-step="1">'
    +   '<div class="dvl-f"><select name="service" id="dvl-service">'+opts+'</select></div>'
    +   '<div class="dvl-f"><div class="dvl-phone"><span class="dvl-cc">🇮🇳 +91</span><input type="tel" name="phone" id="dvl-phone" inputmode="numeric" maxlength="11" placeholder="Enter phone number" autocomplete="tel"></div></div>'
    +   '<div class="dvl-note">'+WA_ICON+'You’ll receive updates on WhatsApp</div>'
    +   '<label class="dvl-consent"><input type="checkbox" id="dvl-consent" checked><span>I agree to DigiVeritaz’s <a href="/terms/" target="_blank" rel="noopener">T&amp;C</a> and <a href="/privacy-policy/" target="_blank" rel="noopener">Privacy Policy</a>. This consent overrides any DNC/NDNC registration.</span></label>'
    +   '<button class="dvl-btn" type="button" id="dvl-proceed">Proceed</button>'
    + '</div>'
    + '<div class="dvl-step" data-step="otp">'
    +   '<p class="dvl-otpinfo">Enter the 6-digit code we sent to <strong id="dvl-otpnum"></strong></p>'
    +   '<div class="dvl-f"><input type="text" id="dvl-otp" inputmode="numeric" maxlength="6" autocomplete="one-time-code" placeholder="······"></div>'
    +   '<div class="dvl-actions"><button class="dvl-back" type="button" data-goto="1">Change number</button><button class="dvl-btn" type="button" id="dvl-verify">Verify &amp; Continue</button></div>'
    +   '<div class="dvl-resendrow">Didn’t get it? <a href="#" id="dvl-resend">Resend code</a></div>'
    + '</div>'
    + '<div class="dvl-step" data-step="2">'
    +   '<div class="dvl-f"><label>Full name</label><input type="text" name="name" id="dvl-name" placeholder="Your full name" autocomplete="name"></div>'
    +   '<div class="dvl-f"><label>Email address</label><input type="email" name="email" id="dvl-email" placeholder="you@company.com" autocomplete="email"></div>'
    +   '<div class="dvl-actions"><button class="dvl-back" type="button" data-goto="1">Back</button><button class="dvl-btn" type="button" id="dvl-continue">Continue</button></div>'
    + '</div>'
    + '<div class="dvl-step" data-step="3">'
    +   '<div class="dvl-f"><label>Company / Website</label><input type="text" name="company" id="dvl-company" placeholder="Company name or website" autocomplete="organization"></div>'
    +   '<div class="dvl-f"><label>Budget Range</label><select name="budget" id="dvl-budget"><option value="">-- Please select budget range --</option><option>INR 40k &ndash; 60k</option><option>INR 60k to 1 Lac</option><option>INR 1 Lac and above</option></select></div>'
    +   '<div class="dvl-f"><label>Select the services you need</label><div class="dvl-checks">'+checks+'</div></div>'
    +   '<div class="dvl-f"><label>What do you need help with?</label><textarea name="message" id="dvl-message" rows="3" placeholder="Goals, budget, timeline, platforms…"></textarea></div>'
    +   '<div class="dvl-actions"><button class="dvl-back" type="button" data-goto="2">Back</button><button class="dvl-btn" type="submit" id="dvl-submit">Submit &amp; Get Proposal</button></div>'
    + '</div>'
    + '<div class="dvl-step" data-step="4">'
    +   '<div class="dvl-thanks"><div class="tick"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg></div>'
    +   '<h3>Thank you! 🎉</h3><p>We’ve got your details and a strategist will reach out within one business day. Keep an eye on WhatsApp.</p></div>'
    + '</div>'
    + '<div class="dvl-err" id="dvl-err"></div>'
    + '</form>';
  }

  function attachForm(root){
    Array.prototype.forEach.call(root.querySelectorAll('[data-goto]'), function(b){ b.addEventListener('click', function(){ go(b.getAttribute('data-goto')); }); });
    $('#dvl-proceed', root).addEventListener('click', onProceed);
    $('#dvl-verify', root).addEventListener('click', onVerify);
    var rs = $('#dvl-resend', root); if (rs) rs.addEventListener('click', otpResend);
    $('#dvl-continue', root).addEventListener('click', onContinue);
    $('.dvl-form', root).addEventListener('submit', onSubmit);
    var ph = $('#dvl-phone', root);
    ph.addEventListener('input', function(){ ph.value = ph.value.replace(/[^0-9]/g,'').slice(0,10); validateStep1(); });
    var otp = $('#dvl-otp', root); if (otp) otp.addEventListener('input', function(){ otp.value = otp.value.replace(/[^0-9]/g,'').slice(0,6); });
    $('#dvl-service', root).addEventListener('change', validateStep1);
    $('#dvl-consent', root).addEventListener('change', validateStep1);
    validateStep1();
  }

  /* ---------- overlay popup mode ---------- */
  function buildModal(){
    if ($('#dvl-overlay')) return;
    injectCSS();
    var ov = document.createElement('div');
    ov.className = 'dvl-overlay'; ov.id = 'dvl-overlay';
    ov.setAttribute('role','dialog'); ov.setAttribute('aria-modal','true'); ov.setAttribute('aria-label','Get your free proposal');
    ov.innerHTML = '<div class="dvl-shell"><header class="dvl-topbar">'+BRAND+'<button class="dvl-close" type="button" aria-label="Close">&times;</button></header>'
                 + '<div class="dvl-body"><div class="dvl-inner">'+formInner()+'</div></div></div>';
    document.body.appendChild(ov);
    $('.dvl-close', ov).addEventListener('click', closeModal);
    attachForm(ov);
  }

  /* ---------- inline page mode ---------- */
  function mountInline(el){
    injectCSS();
    formStart = Date.now();   /* anti-spam _ts: measure dwell from form-mount, not page-load */
    el.innerHTML = '<div class="dvl-page"><header class="dvl-topbar">'+BRAND+'</header>'
                 + '<div class="dvl-body"><div class="dvl-inner">'+formInner()+'</div></div></div>';
    inline = true;
    if (!leadId) { leadId = 'dvl-' + DVL_LOAD.toString(36) + '-' + Math.random().toString(36).slice(2,8); }
    jsok = 'dv-' + Math.random().toString(36).slice(2,12);
    attachForm(el);
    warmMsg91();
    go(1);
  }

  /* ---------- step logic ---------- */
  function err(t){ var e=$('#dvl-err'); if(e) e.textContent = t||''; }
  function steps(n){ var d=document.querySelectorAll('.dvl-steps i'); for(var i=0;i<d.length;i++) d[i].classList.toggle('on', i < n); }
  function progressFor(n){ n=String(n); if(n==='otp')return 1; if(n==='2')return 2; if(n==='3'||n==='4')return 3; return 1; }
  function go(n){
    step = n;
    var all = document.querySelectorAll('.dvl-step');
    for (var i=0;i<all.length;i++) all[i].classList.toggle('is-active', String(n) === all[i].getAttribute('data-step'));
    steps(progressFor(n)); err('');
    var body = $('.dvl-body'); if (body) body.scrollTop = 0;
    var f = document.querySelector('.dvl-step.is-active input, .dvl-step.is-active select, .dvl-step.is-active textarea');
    if (f) { try { f.focus({preventScroll:true}); } catch(e){} }
  }

  function phoneOk(v){ return /^[6-9][0-9]{9}$/.test(String(v||'').replace(/[^0-9]/g,'')); }
  function emailOk(v){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v||'').trim()); }

  function validateStep1(){
    var ok = !!($('#dvl-service')||{}).value && phoneOk(($('#dvl-phone')||{}).value) && ($('#dvl-consent')||{}).checked;
    var b = $('#dvl-proceed'); if (b) b.disabled = !ok;
    return ok;
  }
  function onProceed(){
    if (!validateStep1()){ err('Pick a service, enter a valid 10-digit number and accept the terms.'); return; }
    state.service = $('#dvl-service').value;
    state.phone = '+91' + $('#dvl-phone').value.replace(/[^0-9]/g,'');
    state.consent = 'Yes';
    save(false);                 /* number trapped immediately, BEFORE any OTP */
    var num = $('#dvl-otpnum'); if (num) num.textContent = '+91 ' + $('#dvl-phone').value.replace(/[^0-9]/g,'');
    go('otp');
    otpSend();
  }

  /* ---- OTP via MSG91 OTP Widget (exposeMethods -> our own UI) ---- */
  var MSG91 = { widgetId: '3666766e6633313737383230', tokenAuth: '520932TU9OQwuB86a3942beP1' };
  var DEV = false; /* always send a REAL OTP via MSG91 — no dev skip */
  var msg91Ready = false, msg91Tried = false;
  function otpDigits(){ return ($('#dvl-phone').value||'').replace(/[^0-9]/g,'').slice(-10); }
  function initMsg91(){
    if (msg91Ready) return true;
    if (typeof window.initSendOTP !== 'function') return false;
    try { window.initSendOTP({ widgetId: MSG91.widgetId, tokenAuth: MSG91.tokenAuth, exposeMethods: true, success: function(){}, failure: function(){} }); msg91Ready = true; } catch(e){}
    return msg91Ready;
  }
  function loadMsg91(cb){
    if (DEV) { cb && cb(false); return; }
    if (initMsg91()) { cb && cb(true); return; }
    var urls = ['https://verify.msg91.com/otp-provider.js','https://verify.phone91.com/otp-provider.js'], i = 0;
    (function attempt(){
      var s = document.createElement('script'); s.src = urls[i]; s.async = true;
      s.onload = function(){ cb && cb(initMsg91()); };
      s.onerror = function(){ i++; if (i < urls.length) attempt(); else { cb && cb(false); } };
      document.head.appendChild(s);
    })();
  }
  function warmMsg91(){ if (!msg91Tried && !DEV){ msg91Tried = true; loadMsg91(function(){}); } }

  function otpSend(){
    if (DEV) { err('Dev/preview: OTP is skipped — any code continues.'); return; }
    err('Sending code…');
    loadMsg91(function(ok){
      if (!ok || typeof window.sendOtp !== 'function') { err('Couldn’t reach verification — tap Verify to continue.'); return; }
      window.sendOtp('91' + otpDigits(), function(){ err(''); }, function(e){ try{console.error('MSG91 sendOtp FAILED:',e);}catch(_){} err('Couldn’t send the code. Tap “Resend code”.'); });
    });
  }
  function otpResend(e){ if(e&&e.preventDefault)e.preventDefault();
    if (DEV) { err('Dev/preview: OTP is skipped.'); return; }
    err('Sending a new code…');
    if (typeof window.retryOtp === 'function') { window.retryOtp(null, function(){ err('A new code has been sent.'); }, function(e){ try{console.error('MSG91 retryOtp FAILED:',e);}catch(_){} err('Could not resend — try again.'); }); }
    else { otpSend(); }
  }
  function onVerify(){
    var code=($('#dvl-otp').value||'').replace(/[^0-9]/g,'');
    if(code.length<4){ err('Enter the code from the SMS.'); return; }
    var btn=$('#dvl-verify'); if(btn) btn.disabled=true; err('Verifying…');
    function cont(tag){ state.otp_verified=(/^yes/i.test(tag)?'yes':'no'); save(false); err(''); if(btn) btn.disabled=false; go(2); }
    if (DEV) { cont('Yes (dev)'); return; }
    if (typeof window.verifyOtp !== 'function') { cont('Unverified (sdk offline)'); return; }
    window.verifyOtp(code, function(){ cont('Yes'); }, function(){ if(btn) btn.disabled=false; err('Incorrect or expired code. Resend and try again.'); });
  }
  function onContinue(){
    var nm = $('#dvl-name').value.trim(), em = $('#dvl-email').value.trim();
    if (!nm){ err('Please enter your name.'); return; }
    if (!emailOk(em)){ err('Please enter a valid email.'); return; }
    state.name = nm; state.email = em;
    save(false); go(3);
  }
  function onSubmit(ev){
    ev.preventDefault();
    /* Enter fires the form submit on ANY step — route it to the current step's
       action so it can't skip OTP/details straight to the thank-you screen. */
    var s = String(step);
    if (s === '1') { onProceed(); return; }
    if (s === 'otp') { onVerify(); return; }
    if (s === '2') { onContinue(); return; }
    if (s !== '3') return;
    state.company = $('#dvl-company').value.trim();
    state.message = $('#dvl-message').value.trim();
    var bud = $('#dvl-budget'); state.budget = bud ? bud.value : '';
    var svc = []; Array.prototype.forEach.call(document.querySelectorAll('.dvl-checks input:checked'), function(c){ svc.push(c.value); });
    state.servicesList = svc;
    completed = true;
    /* save() FIRST — it uses navigator.sendBeacon (fetch keepalive fallback), which the
       browser delivers even after we navigate away, so the Apps Script lead write and the
       automated email to the form filler are NOT affected by the redirect below. */
    save(true);
    go(4);
    try { (window.dataLayer = window.dataLayer || []).push({ event:'lead_submitted', form_location: (inline ? 'proposal' : 'popup'), lead_id: leadId }); } catch(e){}
    /* Every completed submission lands on the dedicated /thank-you/ page so the
       conversion can be tracked on a real URL (GTM/GA4). Step 4 shows for a beat
       first so the user sees confirmation even if the redirect is slow.
       src/lid let the thank-you page de-duplicate (transaction_id) so refreshes
       and bookmark hits don't inflate the conversion count. */
    setTimeout(function(){
      try {
        location.href = THANKYOU_URL + '?src=' + (inline ? 'proposal' : 'popup') + '&lid=' + encodeURIComponent(leadId);
      } catch(e){}
    }, 400);
  }

  /* progressive, reliable save — survives page close via sendBeacon */
  function save(complete){
    try{
      var body = new URLSearchParams();
      body.set('action','lead_save');
      body.set('leadId', leadId);
      body.set('complete', complete ? '1' : '');
      body.set('status', complete ? 'Complete' : 'Partial');
      body.set('_source', inline ? 'get-proposal-page' : 'website-popup-v2');
      body.set('_page', location.pathname || '/');
      body.set('_ts', String(formStart || DVL_LOAD));
      body.set('_jsok', jsok);
      body.set('_subject', complete ? 'New FULL lead — DigiVeritaz' : 'New lead (number captured) — DigiVeritaz');
      /* standardized field names — identical to the contact form / DV-POPUP / chatbot */
      if (state.fullname || state.name) body.set('fullname', state.fullname || state.name);
      if (state.phone) body.set('phone', state.phone);
      if (state.email) body.set('email', state.email);
      if (state.company) body.set('company', state.company);
      if (state.message) body.set('message', state.message);
      if (state.consent) body.set('consent', state.consent);
      if (state.budget) body.set('budget', state.budget);
      /* services[] = step-1 primary interest + any step-3 checkboxes (deduped) */
      var svcSet = [];
      if (state.service) svcSet.push(state.service);
      if (state.servicesList && state.servicesList.length) state.servicesList.forEach(function(s){ if (svcSet.indexOf(s) < 0) svcSet.push(s); });
      svcSet.forEach(function(s){ body.append('services[]', s); });
      if (state.otp_verified) body.set('otp_verified', state.otp_verified);
      var ok = false;
      try { ok = !!(navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, new Blob([body.toString()], {type:'application/x-www-form-urlencoded;charset=UTF-8'}))); } catch(e){}
      if (!ok) { fetch(ENDPOINT, { method:'POST', body: body, mode:'no-cors', keepalive:true }).catch(function(){}); }
      savedOnce = true;
    }catch(e){}
  }
  function rescueCapture(){
    if (savedOnce || completed) return;
    var ph = $('#dvl-phone'); if (ph && phoneOk(ph.value)) {
      if (!leadId) leadId = 'dvl-' + DVL_LOAD.toString(36) + '-' + Math.random().toString(36).slice(2,8);
      if (!jsok) jsok = 'dv-' + Math.random().toString(36).slice(2,12);
      state.phone = '+91' + ph.value.replace(/[^0-9]/g,'');
      var sv = $('#dvl-service'); if (sv && sv.value) state.service = sv.value;
      save(false);
    }
  }

  function openModal(){
    buildModal();
    formStart = Date.now();   /* anti-spam _ts: measure dwell from form-open, not page-load */
    var ov = $('#dvl-overlay'); if (!ov) return;
    if (!leadId) { leadId = 'dvl-' + DVL_LOAD.toString(36) + '-' + Math.random().toString(36).slice(2,8); }
    jsok = 'dv-' + Math.random().toString(36).slice(2,12);
    ov.classList.add('is-open'); document.body.classList.add('dvl-lock');
    warmMsg91();
    go(step || 1);
  }
  function closeModal(){
    rescueCapture();
    var ov = $('#dvl-overlay'); if (!ov) return;
    ov.classList.remove('is-open'); document.body.classList.remove('dvl-lock');
  }

  document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && !inline) closeModal(); });
  window.addEventListener('pagehide', rescueCapture);
  document.addEventListener('visibilitychange', function(){ if (document.visibilityState === 'hidden') rescueCapture(); });

  /* triggers — every conversion CTA on every page OPENS the popup (overlay) */
  var PROPOSAL_URL = '/get-proposal/';
  var CTA_RE = /book a call|proposal|get started|get a quote|request a quote|free quote|talk to us|talk to an expert|get in touch|book a demo|consultation|strategy call|grow my|scale my|claim my/i;
  function wire(){
    var nodes = document.querySelectorAll('a.btn, button.btn, a.dvl-trigger, .dvl-open, .dv-m-call, .pv-cta, .dvh-clients-link');
    Array.prototype.forEach.call(nodes, function(el){
      if (el.__dvlWired) return;
      var t = (el.textContent || '').trim().toLowerCase();
      var hit = CTA_RE.test(t) || el.classList.contains('dvl-open') || el.classList.contains('dvl-trigger') || el.classList.contains('dv-m-call') || el.classList.contains('pv-cta') || el.classList.contains('dvh-clients-link');
      if (hit) {
        el.__dvlWired = true; el.classList.add('dv-shine');
        el.addEventListener('click', function(e){ e.preventDefault(); e.stopImmediatePropagation(); openModal(); }, true);
      }
    });
  }
  window.dvOpenModal = function(){ try { openModal(); } catch(e){} };

  /* delegated safety net — catch CTAs injected after wire() runs (capture phase) */
  document.addEventListener('click', function(e){
    var a = e.target && e.target.closest && e.target.closest('.dvl-open, .dvl-trigger, .pv-cta, .dvh-clients-link');
    if (a) { e.preventDefault(); e.stopImmediatePropagation(); try { openModal(); } catch(x){} }
  }, true);

  function ready(){
    var host = document.getElementById('dvl-inline');
    if (host) { mountInline(host); return; }   /* standalone page — no popup, no auto-open */
    wire();
    setTimeout(wire, 1200);
    /* no auto-open here — the wide popup (main.js) handles the one-time auto-open */
  }
  if (document.readyState !== 'loading') ready();
  else document.addEventListener('DOMContentLoaded', ready);
})();
