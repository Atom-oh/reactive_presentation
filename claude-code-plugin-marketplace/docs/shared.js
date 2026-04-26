// === Shared JS for Claude Code Plugin Marketplace Tech Talk ===
(function() {
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  function isActive(href) { return currentPage === href ? ' active' : ''; }

  const pages = [
    { section: 'Overview', items: [
      { href: 'index.html', icon: 'home', label: 'Introduction' }
    ]},
    { section: 'Plugin Engineering', items: [
      { href: '01-why.html', num: '1', label: 'Why — oh-my-cloud-skills' },
      { href: '02-plugin-structure.html', num: '2', label: 'Plugin Architecture' },
      { href: '03-harness.html', num: '3', label: 'Harness Engineering' },
    ]},
    { section: 'Remarp Framework', items: [
      { href: '04-remarp.html', num: '4', label: 'Remarp Framework' },
      { href: '05-vscode-extension.html', num: '5', label: 'VSCode Extension' },
    ]},
    { section: 'Productivity', items: [
      { href: '06-ttobak.html', num: '6', label: 'Ttobak AI Assistant' },
      { href: '07-lessons.html', num: '7', label: 'Lessons Learned' },
    ]},
  ];

  // Build sidebar using safe DOM methods
  function buildSidebar() {
    const el = document.getElementById('sidebar');
    if (!el) return;

    // Header
    const header = document.createElement('div');
    header.className = 'sidebar-header';
    header.textContent = 'Claude Code Plugin Marketplace';
    const subtitle = document.createElement('br');
    header.appendChild(subtitle);
    const sub = document.createElement('span');
    sub.className = 'subtitle';
    sub.textContent = 'Lightning Tech Talk';
    header.appendChild(sub);
    el.appendChild(header);

    // Nav
    const nav = document.createElement('nav');
    nav.className = 'sidebar-nav';
    pages.forEach(sec => {
      const section = document.createElement('div');
      section.className = 'sidebar-section';
      const title = document.createElement('div');
      title.className = 'sidebar-section-title';
      title.textContent = sec.section;
      section.appendChild(title);
      sec.items.forEach(p => {
        const a = document.createElement('a');
        a.href = p.href;
        a.className = 'sidebar-link' + isActive(p.href);
        if (p.num) {
          const badge = document.createElement('span');
          badge.className = 'part-num';
          badge.textContent = p.num;
          a.appendChild(badge);
        }
        a.appendChild(document.createTextNode(' ' + p.label));
        section.appendChild(a);
      });
      nav.appendChild(section);
    });
    el.appendChild(nav);

    // Footer with theme toggle
    const footer = document.createElement('div');
    footer.className = 'sidebar-footer';
    const btn = document.createElement('button');
    btn.onclick = toggleTheme;
    const label = document.createElement('span');
    label.className = 'theme-label';
    label.textContent = 'Dark';
    btn.appendChild(label);
    footer.appendChild(btn);
    el.appendChild(footer);
  }

  function toggleTheme() {
    const t = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('research-theme', t);
    updateThemeIcon();
  }
  window.toggleTheme = toggleTheme;

  function updateThemeIcon() {
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    const label = document.querySelector('.theme-label');
    if (label) label.textContent = dark ? 'Dark' : 'Light';
  }

  window.toggleSidebar = function() {
    document.querySelector('.sidebar').classList.toggle('open');
    document.querySelector('.sidebar-overlay').classList.toggle('open');
  };

  function updateProgress() {
    const bar = document.querySelector('.progress-bar');
    if (!bar) return;
    const scroll = window.scrollY;
    const height = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = height > 0 ? (scroll / height * 100) + '%' : '0%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });

  const saved = localStorage.getItem('research-theme');
  if (saved) { document.documentElement.setAttribute('data-theme', saved); updateThemeIcon(); }

  buildSidebar();
})();
