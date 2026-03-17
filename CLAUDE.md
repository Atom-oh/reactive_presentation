# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A presentation hub serving interactive HTML slideshows. No build tools — pure HTML/CSS/JS. Each presentation is a self-contained subfolder with its own `common/` copy of the framework assets.

## Architecture

```
index.html                    → Hub page listing all presentations
common/                       → Framework used by the hub page (root index.html)
  theme.css                   → Dark theme, 16:9, CSS custom properties (--accent, --bg-primary, etc.)
  slide-framework.js          → SlideFramework class: keyboard/touch nav, progress bar, presenter view
  presenter-view.js           → PresenterView class: dual-window sync via BroadcastChannel
  animation-utils.js          → Canvas primitives: setupCanvas, drawBox, drawArrow, AnimationLoop
  quiz-component.js           → QuizManager: auto-grading with data-quiz/data-correct attributes
{slug}/                       → One presentation per folder
  common/                     → Per-project copy of framework (independent versioning)
  index.html                  → TOC page with block cards + timeline
  01-block-name.html          → Block file (self-contained slides)
```

Each project has its own `common/` folder so framework changes for one presentation don't break others. HTML files reference `common/` (not `common/`).

## Slide HTML Pattern

Every block HTML file follows this structure. Framework files load in this exact order:

```html
<link rel="stylesheet" href="common/theme.css">
<!-- optional: <link rel="stylesheet" href="common/theme-override.css"> -->

<div class="slide-deck">
  <div class="slide title-slide"><h1>Title</h1></div>
  <div class="slide">
    <div class="slide-header"><h2>Heading</h2></div>
    <div class="slide-body"><!-- content --></div>
  </div>
</div>

<script src="common/animation-utils.js"></script>
<script src="common/slide-framework.js"></script>
<script src="common/quiz-component.js"></script>
<script src="common/presenter-view.js"></script>
<script>
  const deck = new SlideFramework({
    footer: 'Optional footer text',
    logoSrc: 'common/pptx-theme/images/logo_1.png',
    presenterNotes: { 1: 'Note for slide 1' },
    onSlideChange: (index, slide) => { /* trigger animations */ }
  });
</script>
```

## Key CSS Classes

Slides use CSS classes from `theme.css` — don't reinvent styles:
- `.slide`, `.slide.active`, `.title-slide` — slide containers
- `.slide-header`, `.slide-body`, `.columns`, `.col-2`, `.col-3` — layout
- `.card`, `.card.highlight`, `.badge-green/yellow/red/blue` — content cards
- `.compare-toggle` + `.compare-btn` + `.compare-content` — comparison toggles
- `.tab-bar` + `.tab-btn` + `.tab-content` — tabbed content
- `.canvas-container` + `.canvas-controls` — canvas wrappers
- `.code-block` with `.comment/.keyword/.string/.key/.value` — syntax highlighting
- `.quiz` + `.quiz-option[data-correct]` + `.quiz-feedback` — quizzes
- `.timeline` + `.timeline-step` + `.timeline-dot` — horizontal timelines
- `.checklist` — click-to-toggle items
- `.pain-quote`, `.callout-info/warning/danger/success` — callouts

## Canvas Animations

Always use `setupCanvas(id, width, height)` for DPR-aware canvas init. Use `AnimationLoop` for requestAnimationFrame management. Every canvas needs Play/Reset buttons.

```javascript
const c = setupCanvas('my-canvas', 1100, 400);
const anim = new AnimationLoop((elapsed) => {
  c.ctx.clearRect(0, 0, c.width, c.height);
  drawBox(c.ctx, x, y, w, h, 'Label', Colors.accent);
});
```

## Commands

```bash
# Serve locally
python3 -m http.server 8080

# Extract PPTX theme (requires python-pptx)
python3 ~/.claude/skills/reactive-presentation/scripts/extract_pptx_theme.py template.pptx -o common/pptx-theme/

# Convert Marp markdown to HTML slides (requires PyYAML)
python3 ~/.claude/skills/reactive-presentation/scripts/marp_to_slides.py content.md -o {slug}/ --theme-dir common/pptx-theme/
```

## Conventions

- All content in Korean, technical terms in English
- All JS inline in a single `<script>` at end of `<body>` (no external JS per slide)
- CSS overrides go in a `<style>` block in `<head>`, not in theme.css
- Slide pacing: ~2-2.5 min per slide, interactive slides ~3-4 min
- Blocks should be 20-35 minutes, with 5 min breaks between
- When adding a new presentation: create folder, add TOC index.html, add card to root index.html
