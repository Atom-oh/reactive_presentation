/* Presenter view: spoken script first, [요약] / [출처] / [약어] below it.
 *
 * Compiled notes read "<cue emoji> [N min] [요약]" bullets, then the script, then optional
 * "[출처]" and "[약어]" paragraphs, each separated by a blank line. On stage the presenter reads
 * the script, so this puts it at the top and moves the summary, sources and abbreviations under
 * a divider in smaller, dimmer text. The cue emoji and "[N min]" stay on a line above the
 * script, and a "↓" in the script (where the presenter presses ↓ for the next step) is drawn as
 * an orange badge. The .md sources are unchanged: only the presenter window's view moves.
 *
 * Same layout as the Claude Code workshop deck (assets/presenter-notes.js there).
 * common/ is overwritten by every build, so this file patches
 * PresenterView.prototype.renderRichNotes at run time. If that method is missing, the notes
 * keep the compiler's order and the console says so.
 */
(function () {
  'use strict';
  if (window.__widPresenterNotes) return;
  window.__widPresenterNotes = true;

  // First line of the summary paragraph, with whatever precedes the tag (cue emoji, [N min]).
  var SUMMARY = /^([^\n]*?)\[요약\]/;
  var META = /^\s*\[(출처|약어)\]/;

  // Split on blank lines; returns null when there is nothing to move.
  function split(text) {
    var paras = String(text).split(/\n[ \t]*\n+/);
    var script = [], meta = [], lead = '';
    for (var i = 0; i < paras.length; i++) {
      var p = paras[i];
      if (!p.trim()) continue;
      var m = SUMMARY.exec(p);
      if (m) {
        lead = m[1].trim();
        meta.push(p.slice(m[1].length));
      } else if (META.test(p)) {
        meta.push(p);
      } else {
        script.push(p);
      }
    }
    if (!meta.length || !script.length) return null;
    // "- " bullets become one <ul> per line in renderRichNotes; "• " keeps the block compact.
    var metaText = meta.join('\n\n').replace(/^[ \t]*-[ \t]+/gm, '• ');
    return { lead: lead, script: script.join('\n\n'), meta: metaText };
  }

  function patch() {
    var PV = window.PresenterView || (typeof PresenterView !== 'undefined' ? PresenterView : null); // eslint-disable-line no-undef
    if (!PV || !PV.prototype) return false;
    if (PV.prototype.__widNotes) return true;
    var orig = PV.prototype.renderRichNotes;
    if (typeof orig !== 'function') return false;
    PV.prototype.renderRichNotes = function (text) {
      var parts = split(text || '');
      var html;
      if (!parts) {
        html = orig.call(this, text);
      } else {
        var top = orig.call(this, parts.script), bottom = orig.call(this, parts.meta);
        var head = parts.lead ? orig.call(this, parts.lead) : '';
        if (typeof top !== 'string' || typeof bottom !== 'string' || typeof head !== 'string') {
          html = orig.call(this, text);
        } else {
          if (head) head = '<div class="wid-notes-lead" style="font-size:0.82em;opacity:0.8;margin-bottom:0.5em;">' + head + '</div>';
          html = head + top +
            '<div class="wid-notes-meta" style="margin-top:1.4em;padding-top:0.9em;border-top:1px solid #2d3250;' +
            'font-size:0.82em;opacity:0.72;">' + bottom + '</div>';
        }
      }
      if (typeof html !== 'string') return html;
      return html.replace(/↓/g, '<span class="wid-step-mark" title="여기서 ↓" style="display:inline-block;' +
        'margin:0 0.15em;padding:0 0.35em;border-radius:4px;background:#ffb454;color:#1a1a2e;' +
        'font-weight:800;line-height:1.3;">↓</span>');
    };
    PV.prototype.__widNotes = true;
    return true;
  }

  var tries = 0;
  (function wait() {
    if (patch()) return;
    if (tries++ < 100) { setTimeout(wait, 100); return; }
    if (typeof console !== 'undefined') {
      console.warn('[presenter-notes] PresenterView.renderRichNotes not found; notes keep the compiler order.');
    }
  })();
})();
