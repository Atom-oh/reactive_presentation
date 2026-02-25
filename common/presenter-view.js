/**
 * Presenter View - Dual window slide presentation with notes, timer, and sync
 * Press 'P' to open presenter view (handled by SlideFramework)
 */
class PresenterView {
  constructor(framework) {
    this.framework = framework;
    this.presenterWindow = null;
    this.channel = new BroadcastChannel('slide-sync');
    this.startTime = null;
    this.timerInterval = null;
    this.windowId = 'main';
    this.setupSync();
  }

  setupSync() {
    this.channel.onmessage = (e) => {
      if (e.data.type === 'goto' && e.data.source !== this.windowId) {
        this.framework.showSlide(e.data.index, true);
        if (this.presenterWindow && !this.presenterWindow.closed) {
          this.updatePresenterView();
        }
      }
    };
  }

  broadcastSlideChange(index) {
    this.channel.postMessage({
      type: 'goto',
      index: index,
      source: this.windowId
    });
  }

  open() {
    if (this.presenterWindow && !this.presenterWindow.closed) {
      this.presenterWindow.focus();
      return;
    }

    const html = this.createPresenterHTML();
    this.presenterWindow = window.open('', 'presenter', 'width=1200,height=800');
    this.presenterWindow.document.write(html);
    this.presenterWindow.document.close();

    if (!this.startTime) {
      this.startTime = Date.now();
    }

    this.setupPresenterControls();
    this.updatePresenterView();
    this.startTimer();
  }

  createPresenterHTML() {
    return `<!DOCTYPE html>
<html><head><title>Presenter View - ${document.title}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #1a1a2e;
    color: #e8eaf0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .presenter-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: #0f0f1a;
    border-bottom: 1px solid #2d3250;
  }
  .presenter-timer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    color: #6c5ce7;
  }
  .presenter-counter {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    color: #9ba1b8;
  }
  .presenter-title {
    font-size: 1rem;
    color: #6b7194;
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .presenter-main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  .presenter-current {
    flex: 3;
    border-right: 1px solid #2d3250;
    position: relative;
    background: #0f1117;
    overflow: hidden;
  }
  .presenter-next {
    flex: 2;
    position: relative;
    background: #0a0a12;
    overflow: hidden;
  }
  .slide-label {
    position: absolute;
    top: 8px;
    left: 12px;
    font-size: 0.75rem;
    color: #6b7194;
    background: rgba(15, 17, 23, 0.9);
    padding: 2px 8px;
    border-radius: 4px;
    z-index: 10;
  }
  .slide-preview {
    width: 100%;
    height: 100%;
    overflow: hidden;
    padding: 16px;
  }
  .presenter-notes {
    height: 200px;
    padding: 16px 20px;
    background: #0f0f1a;
    border-top: 1px solid #2d3250;
    overflow-y: auto;
  }
  .presenter-notes h3 {
    font-size: 0.85rem;
    color: #6b7194;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .presenter-notes .notes-content {
    font-size: 1rem;
    line-height: 1.6;
    color: #c8cad0;
    white-space: pre-wrap;
  }
  .presenter-nav {
    display: flex;
    justify-content: center;
    gap: 12px;
    padding: 10px;
    background: #0f0f1a;
    border-top: 1px solid #2d3250;
  }
  .presenter-nav button {
    padding: 8px 24px;
    border: 1px solid #2d3250;
    border-radius: 6px;
    background: #232740;
    color: #e8eaf0;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 150ms ease;
  }
  .presenter-nav button:hover {
    background: #2d3250;
    border-color: #6c5ce7;
  }
  .end-message {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #6b7194;
    font-style: italic;
  }
</style>
</head><body>
<div class="presenter-topbar">
  <span class="presenter-title" id="p-title"></span>
  <span class="presenter-timer" id="p-timer">00:00:00</span>
  <span class="presenter-counter" id="p-counter"></span>
</div>
<div class="presenter-main">
  <div class="presenter-current">
    <span class="slide-label">Current Slide</span>
    <div class="slide-preview" id="p-current"></div>
  </div>
  <div class="presenter-next">
    <span class="slide-label">Next Slide</span>
    <div class="slide-preview" id="p-next"></div>
  </div>
</div>
<div class="presenter-notes">
  <h3>Speaker Notes</h3>
  <div class="notes-content" id="p-notes">No notes for this slide.</div>
</div>
<div class="presenter-nav">
  <button id="p-prev">← Previous</button>
  <button id="p-next-btn">Next →</button>
</div>
</body></html>`;
  }

  setupPresenterControls() {
    const win = this.presenterWindow;
    const doc = win.document;

    doc.getElementById('p-prev').onclick = () => {
      this.framework.prev();
      this.broadcastSlideChange(this.framework.currentSlide);
      this.updatePresenterView();
    };

    doc.getElementById('p-next-btn').onclick = () => {
      this.framework.next();
      this.broadcastSlideChange(this.framework.currentSlide);
      this.updatePresenterView();
    };

    doc.addEventListener('keydown', (e) => {
      switch (e.key) {
        case 'ArrowRight':
        case ' ':
          e.preventDefault();
          this.framework.next();
          this.broadcastSlideChange(this.framework.currentSlide);
          this.updatePresenterView();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          this.framework.prev();
          this.broadcastSlideChange(this.framework.currentSlide);
          this.updatePresenterView();
          break;
      }
    });

    doc.getElementById('p-title').textContent = document.title;
  }

  updatePresenterView() {
    if (!this.presenterWindow || this.presenterWindow.closed) return;

    const doc = this.presenterWindow.document;
    const idx = this.framework.currentSlide;
    const slides = this.framework.slides;

    doc.getElementById('p-counter').textContent = `${idx + 1} / ${this.framework.totalSlides}`;

    const currentEl = doc.getElementById('p-current');
    const currentClone = slides[idx].cloneNode(true);
    currentClone.style.cssText = `
      position: relative;
      display: flex;
      flex-direction: column;
      padding: 24px 32px;
      height: 100%;
      opacity: 1;
      font-size: 0.65em;
      overflow: hidden;
      background: #0f1117;
      color: #e8eaf0;
    `;
    currentEl.innerHTML = '';
    currentEl.appendChild(currentClone);

    const nextEl = doc.getElementById('p-next');
    nextEl.innerHTML = '';
    if (idx + 1 < slides.length) {
      const nextClone = slides[idx + 1].cloneNode(true);
      nextClone.style.cssText = `
        position: relative;
        display: flex;
        flex-direction: column;
        padding: 16px 24px;
        height: 100%;
        opacity: 0.7;
        font-size: 0.5em;
        overflow: hidden;
        background: #0a0a12;
        color: #e8eaf0;
      `;
      nextEl.appendChild(nextClone);
    } else {
      const endMsg = doc.createElement('div');
      endMsg.className = 'end-message';
      endMsg.textContent = 'End of presentation';
      nextEl.appendChild(endMsg);
    }

    const noteKey = idx + 1;
    const notes = (this.framework.presenterNotes || {})[noteKey] || 'No notes for this slide.';
    doc.getElementById('p-notes').textContent = notes;
  }

  startTimer() {
    if (this.timerInterval) return;

    this.timerInterval = setInterval(() => {
      if (!this.presenterWindow || this.presenterWindow.closed) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
        return;
      }
      const elapsed = Date.now() - this.startTime;
      const el = this.presenterWindow.document.getElementById('p-timer');
      if (el) el.textContent = this.formatTime(elapsed);
    }, 1000);
  }

  formatTime(ms) {
    const s = Math.floor(ms / 1000);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  }

  destroy() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
    if (this.presenterWindow && !this.presenterWindow.closed) {
      this.presenterWindow.close();
    }
    this.channel.close();
  }
}
