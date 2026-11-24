/* Links between the main slides and the appendix.
 *
 * <a data-wid-goto="04-appendix:4" href="./04-appendix.html#4">...</a>
 *   In index.html (all blocks on one page) the link jumps in place with deck.goTo(), so the
 *   presenter window stays connected. In a single block file the target block is not on the
 *   page, so the plain href opens that block's file at the slide number.
 * Before jumping, the current page and slide are remembered; a "본편으로 돌아가기" button then
 * stays on screen until the presenter is back on that slide, and returns there when clicked.
 *
 * Styles live here because common/ is overwritten by every build.
 */
(function () {
  'use strict';
  if (window.__widAppendixLinks) return;
  window.__widAppendixLinks = true;
  var KEY = 'wid-return';

  var css = '' +
    '.wid-applinks{display:flex;flex-wrap:wrap;gap:var(--space-2,8px);margin-top:var(--space-2,8px);}' +
    'a.wid-applink{display:inline-flex;align-items:center;gap:.3em;padding:.15em .7em;border:1px solid var(--border,#3a4150);' +
    'border-radius:999px;font-size:var(--fs-caption,.8em);color:var(--on-surface-muted,#9aa4b2);text-decoration:none;}' +
    'a.wid-applink:hover{color:var(--accent,#ff9900);border-color:var(--accent,#ff9900);}' +
    // Fixed colours: the button sits outside the deck, so the theme variables do not reach it.
    '#wid-return{position:fixed;right:24px;bottom:132px;z-index:50;padding:.45em 1em;border-radius:999px;' +
    'border:1px solid #ff9900;background:#232f3e;color:#ffffff;box-shadow:0 2px 8px rgba(0,0,0,.35);' +
    'font:600 15px/1.2 system-ui,sans-serif;cursor:pointer;display:none;}';
  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  function store(v) {
    try { if (v) sessionStorage.setItem(KEY, JSON.stringify(v)); else sessionStorage.removeItem(KEY); } catch (e) { /* private mode */ }
  }
  function load() {
    try { return JSON.parse(sessionStorage.getItem(KEY) || 'null'); } catch (e) { return null; }
  }
  function fw() { return (typeof deck !== 'undefined' && deck && deck.goTo) ? deck : null; } // eslint-disable-line no-undef
  function slides() { return Array.prototype.slice.call(document.querySelectorAll('.slide-deck .slide')); }
  function fileOf(path) { return path.split('/').pop() || 'index.html'; }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-wid-goto]');
    if (a) {
      var f = fw();
      var spec = a.getAttribute('data-wid-goto').split(':');
      var n = parseInt(spec[1], 10);
      store({ path: location.pathname, idx: f ? f.currentSlide : 0 });
      var all = slides();
      var inBlock = all.filter(function (s) { return s.dataset.block === spec[0]; });
      if (f && n >= 1 && inBlock.length >= n) {
        e.preventDefault();
        f.goTo(all.indexOf(inBlock[n - 1]));
      }
      return; // otherwise the href opens the block file
    }
    var r = e.target.closest && e.target.closest('#wid-return');
    if (r) {
      e.preventDefault();
      var back = load();
      store(null);
      r.style.display = 'none';
      if (!back) return;
      var g = fw();
      if (back.path === location.pathname && g) g.goTo(back.idx);
      else location.href = './' + fileOf(back.path) + '#' + (back.idx + 1);
    }
  });

  var btn = document.createElement('button');
  btn.id = 'wid-return';
  btn.type = 'button';
  btn.textContent = '본편으로 돌아가기';
  // Shown after any jump until the presenter is back on the slide the jump started from.
  function sync() {
    var back = load(), f = fw();
    var atOrigin = back && f && back.path === location.pathname && f.currentSlide === back.idx;
    if (atOrigin) store(null);
    btn.style.display = back && !atOrigin ? 'block' : 'none';
  }
  document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(btn); sync(); });
  if (document.readyState !== 'loading') { document.body.appendChild(btn); setTimeout(sync, 0); }
  document.addEventListener('rp:slidechange', sync);
})();
