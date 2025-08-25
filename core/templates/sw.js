/* ERP_CORE — Service Worker (root scope) */
/* الحفظ على المنطق القائم + توسعة وتحسينات فقط */

const CACHE_PREFIX = "erp-core-cache-";
const CACHE_NAME   = "erp-core-cache-v2025.08.16";
const OFFLINE_URL  = "/offline.html";

/* ملفات موجودة فعليًا عندك (الإبقاء كما هي) */
const ASSETS_TO_CACHE = [
  "/",
  OFFLINE_URL,
  "/static/css/erp.css",
  "/static/css/odoo-palette.css",
  "/static/js/erp.js",
  "/static/js/main.js",
  "/static/icons/icon-192x192.png",
  "/static/icons/icon-512x512.png",
];

/* ✅ تحسين: قناة بث لإشعارات التفعيل/الإصدار (لا تؤثر إن لم تُستخدم) */
let bc = null;
try { bc = new BroadcastChannel('erp-sw'); } catch(_) {}

/* تثبيت: نحاول نحمل كل ملف ونتجاهل الفاشل */
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      await Promise.all(
        ASSETS_TO_CACHE.map(async (url) => {
          try {
            const resp = await fetch(url, { cache: "no-cache" });
            if (resp.ok) await cache.put(url, resp.clone());
          } catch (_) { /* تجاهل الملف المفقود */ }
        })
      );
    })
  );
  self.skipWaiting();
});

/* تفعيل: امسح الكاشات القديمة + فعّل navigationPreload لتحسين الأداء */
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    try {
      if (self.registration.navigationPreload) {
        await self.registration.navigationPreload.enable();
      }
    } catch (_) {}
    const keys = await caches.keys();
    await Promise.all(keys.map(k => (k === CACHE_NAME || !k.startsWith(CACHE_PREFIX)) ? null : caches.delete(k)));
    await self.clients.claim();
    try { bc && bc.postMessage({type:'SW_ACTIVATED', value: CACHE_NAME}); } catch(_) {}
  })());
});

/* استراتيجية الجلب:
   - navigation: شبكة أولاً (مع استخدام navigationPreload إن توفّر)، ولو أوفلاين نعرض offline.html
   - باقي GET من نفس الأصل: Stale-While-Revalidate
*/
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);
  if (url.origin !== location.origin) return;
  if (url.pathname === "/sw.js") return; // لا نتدخل في ملف الـ SW نفسه

  if (event.request.mode === "navigate") {
    event.respondWith((async () => {
      try {
        const preload = await event.preloadResponse;
        if (preload) return preload;
      } catch(_) {}
      try {
        return await fetch(event.request);
      } catch(_) {
        return await caches.match(OFFLINE_URL) || Response.error();
      }
    })());
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const fetchAndUpdate = fetch(event.request)
        .then((resp) => {
          if (resp && resp.status === 200) {
            const clone = resp.clone();
            caches.open(CACHE_NAME).then((c) => c.put(event.request, clone));
          }
          return resp;
        })
        .catch(() => cached);
      return cached || fetchAndUpdate;
    })
  );
});

/* رسائل بين الصفحة و SW */
self.addEventListener("message", (event) => {
  try{
    if (!event.data) return;
    if (event.data.type === "SKIP_WAITING") { self.skipWaiting(); }
    if (event.data.type === "GET_VERSION") {
      event.source && event.source.postMessage({type:"SW_VERSION", value: CACHE_NAME});
      bc && bc.postMessage({type:"SW_VERSION", value: CACHE_NAME});
    }
  }catch(_){}
});

/* اختيارية — دعم Push/SYNC (لن تعمل إلا إذا فُعّلت من السيرفر) */
self.addEventListener('push', (e) => {
  // لا تغيير للسلوك الافتراضي — مجرد دعم اختياري
  if (!e.data) return;
  const payload = (()=>{ try{ return e.data.json(); }catch(_){ return {title:'ERP', body:e.data.text()}; }})();
  e.waitUntil(self.registration.showNotification(payload.title || 'ERP', {
    body: payload.body || '',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-192x192.png',
    data: payload.data || {}
  }));
});

self.addEventListener('sync', (e) => {
  // مكان مخصص لمهام المزامنة الخلفية إن لزم
  // مثال: if (e.tag === 'sync-outbox') { e.waitUntil(processOutbox()); }
});
