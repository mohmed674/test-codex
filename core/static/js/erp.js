/* ===== ERP Core — Global JS (RTL/EN + Theme + UX) ===== */
(function () {
  'use strict';
  const LS = window.localStorage;
  const THEME_KEY = 'erp-theme';
  const SIDEBAR_KEY = 'erp-sidebar';

  // ---------- Theme (light/dark/system) ----------
  function prefersDark() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function applyTheme(mode) {
    const root = document.documentElement;
    if (mode === 'dark' || mode === 'light') {
      root.setAttribute('data-theme', mode);
    } else {
      root.setAttribute('data-theme', prefersDark() ? 'dark' : 'light');
    }
  }
  function cycleTheme(cur) { return cur === 'dark' ? 'light' : cur === 'light' ? 'system' : 'dark'; }
  function updateThemeButton(btn, mode) {
    btn.dataset.theme = mode;
    const i = btn.querySelector('i');
    if (!i) return;
    i.classList.remove('fa-moon', 'fa-sun', 'fa-circle-half-stroke');
    i.classList.add(mode === 'dark' ? 'fa-sun' : mode === 'light' ? 'fa-circle-half-stroke' : 'fa-moon');
  }
  function initTheme() {
    const saved = LS.getItem(THEME_KEY) || 'system';
    applyTheme(saved);
    if (saved === 'system' && window.matchMedia) {
      try {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => applyTheme('system'));
      } catch (e) {}
    }
    const btn = document.getElementById('themeToggle') || document.querySelector('[data-theme-toggle]');
    if (btn) {
      btn.addEventListener('click', () => {
        const next = cycleTheme(LS.getItem(THEME_KEY) || 'system');
        LS.setItem(THEME_KEY, next);
        applyTheme(next);
        updateThemeButton(btn, next);
      });
      updateThemeButton(btn, saved);
    }
  }

  // ---------- Sidebar toggle (state sync + persistence; click handled in base template) ----------
  function initSidebar() {
    const saved = LS.getItem(SIDEBAR_KEY);
    if (saved === 'open') document.body.classList.add('sidebar-open');
    if (saved === 'closed') document.body.classList.remove('sidebar-open');

    const aside = document.getElementById('erpSidebar');
    const syncAside = () => {
      if (!aside) return;
      if (document.body.classList.contains('sidebar-open')) aside.setAttribute('data-open', '');
      else aside.removeAttribute('data-open');
    };
    syncAside();

    // Observe body class changes (toggled elsewhere) to persist + sync aside
    try {
      new MutationObserver(() => {
        syncAside();
        try { LS.setItem(SIDEBAR_KEY, document.body.classList.contains('sidebar-open') ? 'open' : 'closed'); } catch (e) {}
      }).observe(document.body, { attributes: true, attributeFilter: ['class'] });
    } catch (e) {}
  }

  // ---------- Slash focus for search ----------
  function initSlash() {
    const target = document.querySelector('[data-slash-focus], #appFilter, #listSearch');
    if (!target) return;
    window.addEventListener('keydown', (e) => {
      const tag = (document.activeElement?.tagName || '').toLowerCase();
      if (e.key === '/' && !/input|textarea|select/.test(tag)) {
        e.preventDefault(); target.focus();
      }
    });
  }

  // ---------- Confirm helper (data-confirm) ----------
  function initConfirm() {
    const ar = document.documentElement.dir === 'rtl';
    const fallback = ar ? 'هل أنت متأكد؟' : 'Are you sure?';
    const externalMsg = document.getElementById('confirm-message')?.textContent; // من json_script لو موجود
    const ask = (el) => {
      const msg = el.getAttribute('data-confirm') || externalMsg || fallback;
      return window.confirm(msg);
    };
    document.querySelectorAll('a[data-confirm]').forEach((a) => {
      a.addEventListener('click', (e) => { if (!ask(a)) e.preventDefault(); });
    });
    document.querySelectorAll('form[data-confirm]').forEach((f) => {
      f.addEventListener('submit', (e) => { if (!ask(f)) e.preventDefault(); });
    });
  }

  // ---------- Column toggles (.col-toggle value=class) ----------
  function initColumns() {
    const table = document.querySelector('table');
    if (!table) return;
    const show = (cls, on) => table.querySelectorAll('.' + cls).forEach((td) => (td.style.display = on ? '' : 'none'));
    document.querySelectorAll('.col-toggle').forEach((chk) => {
      show(chk.value, chk.checked);
      chk.addEventListener('change', () => show(chk.value, chk.checked));
    });
  }

  // ---------- Density (.density-btn) ----------
  function initDensity() {
    const wrap = document.querySelector('.table-responsive');
    if (!wrap) return;
    const key = document.body.getAttribute('data-density-key') || (document.title || 'erp') + ':density';
    const saved = LS.getItem(key) || 'normal';
    wrap.classList.add('density-' + saved);
    document.querySelectorAll('.density-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        wrap.classList.remove('density-compact', 'density-normal', 'density-comfort');
        const v = btn.dataset.density || 'normal';
        wrap.classList.add('density-' + v);
        LS.setItem(key, v);
      });
    });
  }

  // ---------- Shortcuts (Ctrl/Cmd+Enter submit, Esc back) ----------
  function initShortcuts() {
    const form = document.querySelector('form');
    const submitBtn = form?.querySelector('[type="submit"]');
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && submitBtn) {
        e.preventDefault(); submitBtn.click();
      } else if (e.key === 'Escape') {
        const back = document.querySelector('.card-header a.btn-outline-secondary,[data-back]');
        if (back) { e.preventDefault(); window.location.href = back.getAttribute('href'); }
      }
    });
  }

  // ---------- Uppercase abbreviation fields ----------
  function initAbbrev() {
    document.querySelectorAll('[name*="abbreviation"],[id*="abbreviation"]').forEach((inp) => {
      inp.addEventListener('input', () => (inp.value = inp.value.toUpperCase()));
    });
  }

  // ---------- Command Palette (Ctrl/Cmd + K) ----------
  function initPalette() {
    const btn = document.getElementById('cmdPaletteBtn');
    const modal = document.getElementById('cmdPalette');
    const input = document.getElementById('cmdInput');
    const list = document.getElementById('cmdList');
    if (!modal || !input || !list) return;

    const baseCmds = [
      { label: 'Overview / نظرة عامة', href: '/core/overview/' },
      { label: 'Apps / التطبيقات', href: '/core/' },
      { label: 'Logout / تسجيل خروج', href: '/accounts/logout/' },
    ];

    const extra = (window.ERP && Array.isArray(window.ERP.commands)) ? window.ERP.commands : [];
    const allCmds = baseCmds.concat(extra);

    function open() {
      modal.hidden = false; input.value = ''; render(''); input.focus();
    }
    function close() { modal.hidden = true; }
    function render(q) {
      const term = q.trim().toLowerCase();
      list.innerHTML = '';
      allCmds.filter(c => !term || c.label.toLowerCase().includes(term)).forEach(c => {
        const div = document.createElement('div');
        div.className = 'item'; div.textContent = c.label;
        div.addEventListener('click', () => { window.location.href = c.href; });
        list.appendChild(div);
      });
      if (!list.children.length) {
        const div = document.createElement('div'); div.className = 'item'; div.textContent = 'No results';
        list.appendChild(div);
      }
    }

    btn && btn.addEventListener('click', open);
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); open(); }
      if (e.key === 'Escape' && !modal.hidden) { e.preventDefault(); close(); }
    });
    input.addEventListener('input', (e) => render(e.target.value));
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
  }

  // ---------- Service Worker (fallback registration if not already registered) ----------
  function initSW() {
    if (!('serviceWorker' in navigator)) return;
    try {
      navigator.serviceWorker.getRegistration().then((reg) => {
        if (reg) return; // Already registered (e.g., by base template)
        navigator.serviceWorker.register('/sw.js').catch(() => {});
      }).catch(() => {});
    } catch (e) {}
  }

  // ---------- Boot ----------
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();
    initSlash();
    initConfirm();
    initColumns();
    initDensity();
    initShortcuts();
    initAbbrev();
    initPalette();
    initSW();
  });
})();
