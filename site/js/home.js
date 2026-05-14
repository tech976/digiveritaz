/* ============================================================
   DigiVeritaz home — premium motion layer
   Loaded only on home-new.html. Pure vanilla, no deps.
   - Scroll reveal (IntersectionObserver, fade + lift)
   - 3D card tilt on hover (subtle, max 5deg)
   - Hero parallax (text & cards drift at different speeds)
   - Impact counter (numbers tick up on enter)
   Respects prefers-reduced-motion + skips on touch.
   ============================================================ */
(function(){
  'use strict';

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouch = window.matchMedia('(hover: none), (pointer: coarse)').matches;

  /* ---------- 1. Scroll reveal ---------- */
  function setupReveal(){
    // Observe both .dvh-reveal (fade-in elements) AND [data-stagger]
    // (cascading child grids). Either pattern needs `.is-in` to be applied.
    const els = document.querySelectorAll('.dvh-reveal, [data-stagger]');
    if(reduce || !('IntersectionObserver' in window)){
      els.forEach(e => e.classList.add('is-in'));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if(e.isIntersecting){
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -60px 0px' });
    els.forEach(e => io.observe(e));
  }

  /* ---------- 2. 3D card tilt on hover ---------- */
  function setupTilt(){
    if(reduce || isTouch) return;
    const cards = document.querySelectorAll('[data-tilt]');
    cards.forEach(card => {
      let rafId = null;
      const reset = () => {
        cancelAnimationFrame(rafId);
        card.style.transform = '';
      };
      card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width;
        const y = (e.clientY - r.top) / r.height;
        const rx = ((y - 0.5) * -5).toFixed(2);
        const ry = ((x - 0.5) *  5).toFixed(2);
        if(rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(() => {
          card.style.transform =
            `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-3px)`;
        });
      });
      card.addEventListener('mouseleave', reset);
      card.addEventListener('blur', reset);
    });
  }

  /* ---------- 3. Hero parallax ---------- */
  function setupParallax(){
    if(reduce || isTouch) return;
    const layers = document.querySelectorAll('[data-parallax]');
    if(!layers.length) return;
    let ticking = false;
    const onScroll = () => {
      if(ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const y = window.scrollY;
        layers.forEach(el => {
          const speed = parseFloat(el.dataset.parallax) || 0.1;
          el.style.transform = `translate3d(0, ${(-y * speed).toFixed(2)}px, 0)`;
        });
        ticking = false;
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- 4. Counter animation on impact numbers ---------- */
  function easeOutExpo(t){return t === 1 ? 1 : 1 - Math.pow(2, -10 * t)}

  function parseTargetFromText(text){
    // Extract first number from strings like "60+", "1.15L+", "4.9★", "94%", "13+"
    const m = text.match(/([\d]+(?:\.[\d]+)?)/);
    return m ? parseFloat(m[1]) : null;
  }

  function animateCounter(el){
    const original = el.textContent.trim();
    const target = parseTargetFromText(original);
    if(target === null) return;
    if(reduce){return}
    // Preserve trailing chars after the number (e.g. "+", "L+", "%", "★")
    const numMatch = original.match(/([\d.]+)(.*)/);
    if(!numMatch) return;
    const num = parseFloat(numMatch[1]);
    const suffix = numMatch[2] || '';
    const decimals = (numMatch[1].split('.')[1] || '').length;
    const dur = 1500;
    const start = performance.now();
    function step(now){
      const t = Math.min(1, (now - start) / dur);
      const v = num * easeOutExpo(t);
      el.textContent = (decimals > 0 ? v.toFixed(decimals) : Math.round(v)) + suffix;
      if(t < 1) requestAnimationFrame(step);
      else el.textContent = original;
    }
    requestAnimationFrame(step);
  }

  function setupCounters(){
    const nums = document.querySelectorAll('.impact-num, .ps-num, .hv-a-trust .tr strong');
    if(!nums.length) return;
    if(reduce || !('IntersectionObserver' in window)){
      // Just leave the original text in place
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if(e.isIntersecting){
          animateCounter(e.target);
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.4 });
    nums.forEach(n => io.observe(n));
  }

  /* ---------- Init ---------- */
  function init(){
    setupReveal();
    setupTilt();
    setupParallax();
    setupCounters();
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
