// === Shared JS for Checkpointless Training Research Docs ===
(function() {
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  function isActive(href) { return currentPage === href ? ' active' : ''; }

  const pages = [
    { section: '개요', items: [
      { href: 'index.html', icon: 'home', label: '소개 & 목차' }
    ]},
    { section: 'Part 1: 기초', items: [
      { href: '01-sagemaker-hyperpod.html', num: '1', label: 'SageMaker & HyperPod' },
      { href: '02-distributed-training.html', num: '2', label: '분산 학습 기초' },
      { href: '03-fsdp-zero-nccl.html', num: '3', label: 'FSDP, ZeRO, NCCL' },
      { href: '04-hardware-networking.html', num: '4', label: 'GPU & EFA 네트워킹' },
    ]},
    { section: 'Part 2: 문제', items: [
      { href: '05-checkpointing.html', num: '5', label: 'Checkpointing 한계' },
    ]},
    { section: 'Part 3: 솔루션', items: [
      { href: '06-checkpointless.html', num: '6', label: 'Checkpointless Training' },
      { href: '07-getting-started.html', num: '7', label: '성능 & Getting Started' },
    ]},
    { section: 'Part 4: 비교 & 참고', items: [
      { href: '08-competitors.html', num: '8', label: '경쟁 기술 & 학술 연구' },
      { href: '09-qa-glossary.html', num: '9', label: 'Q&A & 용어집' },
    ]},
  ];

  let navHTML = '';
  pages.forEach(sec => {
    navHTML += `<div class="sidebar-section"><div class="sidebar-section-title">${sec.section}</div>`;
    sec.items.forEach(p => {
      const numBadge = p.num ? `<span class="part-num">${p.num}</span>` : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`;
      navHTML += `<a href="${p.href}" class="sidebar-link${isActive(p.href)}">${numBadge} ${p.label}</a>`;
    });
    navHTML += '</div>';
  });

  const sidebarHTML = `
    <div class="sidebar-header">
      Checkpointless Training<br><span class="subtitle">Deep Research Document</span>
    </div>
    <nav class="sidebar-nav">${navHTML}</nav>
    <div class="sidebar-footer">
      <button onclick="toggleTheme()">
        <svg class="moon-icon" viewBox="0 0 24 24" width="14" height="14"><path d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"/></svg>
        <span class="theme-label">Dark</span>
      </button>
    </div>
  `;

  const el = document.getElementById('sidebar');
  if (el) el.innerHTML = sidebarHTML;

  // Theme
  window.toggleTheme = function() {
    const t = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('research-theme', t);
    updateThemeIcon();
  };
  function updateThemeIcon() {
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    const label = document.querySelector('.theme-label');
    if (label) label.textContent = dark ? 'Dark' : 'Light';
  }

  // Mobile sidebar
  window.toggleSidebar = function() {
    document.querySelector('.sidebar').classList.toggle('open');
    document.querySelector('.sidebar-overlay').classList.toggle('open');
  };

  // Progress bar
  function updateProgress() {
    const bar = document.querySelector('.progress-bar');
    if (!bar) return;
    const scroll = window.scrollY;
    const height = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = height > 0 ? (scroll / height * 100) + '%' : '0%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });

  // Init
  const saved = localStorage.getItem('research-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon();
  updateProgress();

  // Build flat page list for prev/next nav
  const flatPages = [];
  pages.forEach(s => s.items.forEach(p => flatPages.push(p)));
  const curIdx = flatPages.findIndex(p => p.href === currentPage);

  const navFooter = document.querySelector('.nav-footer');
  if (navFooter && curIdx >= 0) {
    const prev = curIdx > 0 ? flatPages[curIdx - 1] : null;
    const next = curIdx < flatPages.length - 1 ? flatPages[curIdx + 1] : null;
    navFooter.innerHTML = (prev
      ? `<a href="${prev.href}"><span class="nav-label">이전</span> ${prev.label}</a>`
      : '<span></span>')
      + (next
      ? `<a href="${next.href}"><span class="nav-label">다음</span> ${next.label}</a>`
      : '<span></span>');
  }
})();
