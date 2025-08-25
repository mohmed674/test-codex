/* ERP_CORE — JavaScript رئيسي لإدارة الواجهة وتحسين التجربة */

// =========================
// ١) سجل بدء التحميل
// =========================
console.log("%cERP Theme Loaded — 2025 Enhanced Edition", "color:#4e73df;font-weight:bold;");

// =========================
// ٢) إعداد تبديل الوضع الليلي/النهاري
// =========================
(function () {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const curTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const nextTheme = curTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('erp_theme', nextTheme);
            this.setAttribute('aria-pressed', String(nextTheme === 'dark'));
        });
    }

    // استعادة الثيم من LocalStorage
    try {
        const savedTheme = localStorage.getItem('erp_theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
    } catch (e) { console.warn("Theme load failed:", e); }
})();

// =========================
// ٣) إشعارات فورية (Toast)
// =========================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `erp-toast toast-${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// =========================
/* ٤) تحسينات الأداء (Lazy Loading للصور) */
// =========================
document.addEventListener("DOMContentLoaded", () => {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    lazyImages.forEach(img => observer.observe(img));
});

// =========================
// ٥) دعم البحث السريع في القوائم
// =========================
function initQuickSearch(inputSelector, listSelector) {
    const input = document.querySelector(inputSelector);
    const list = document.querySelectorAll(listSelector);
    if (!input) return;
    input.addEventListener('input', function () {
        const q = this.value.toLowerCase();
        list.forEach(item => {
            item.style.display = item.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
    });
}

// =========================
// ٦) دعم PWA (Service Worker) — توحيد التسجيل دون حذف الموجود
// =========================
(function(){
  if (!('serviceWorker' in navigator)) return;

  const link = document.querySelector('link[rel="serviceworker"]');
  const primary = (link && link.getAttribute('href')) || '/sw.js';
  const fallback = (function(){ try { return document.querySelector('link[rel="icon"][href*="static"]') ? '/static/sw.js' : "{% static 'sw.js' %}"; } catch(_) { return "{% static 'sw.js' %}"; } })();

  function registerAt(url){
    return navigator.serviceWorker.register(url).then(function(reg){
      // تحسين: طلب التحديث عند دخول الصفحة
      try { reg.update(); } catch(e){}
      return reg;
    });
  }

  registerAt(primary).catch(function(){
    if (primary !== fallback) { return registerAt(fallback); }
  });
})();

// =========================
// ٧) دعم اختصارات لوحة المفاتيح
// =========================
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const searchBox = document.querySelector('#quickSearch');
        if (searchBox) searchBox.focus();
    }
});
