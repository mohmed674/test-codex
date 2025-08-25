/* ERP_CORE — Service Worker (root scope) */

/* غيّر الإصدار لما تحدّث علشان نجبر التحديث */
const CACHE_NAME = "erp-core-cache-v2025.08.16";
const OFFLINE_URL = "/offline.html";

/* ملفات موجودة فعليًا عندك */
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

/* تثبيت: نحاول نحمل كل ملف ونتجاهل اللي يفشل (ما نعطلش SW) */
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      await Promise.all(
        ASSETS_TO_CACHE.map(async (url) => {
          try {
            const resp = await fetch(url, { cache: "no-cache" });
            if (resp.ok) await cache.put(url, resp.clone());
          } catch (_) {
            /* تجاهل الملف المفقود */
          }
        })
      );
    })
  );
  self.skipWaiting();
});

/* تفعيل: امسح الكاشات القديمة */
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (k === CACHE_NAME ? null : caches.delete(k))))
    )
  );
  self.clients.claim();
});

/* fetch:
   - للـ navigation: شبكة أولاً، ولو أوفلاين نعرض offline.html
   - لباقي GET من نفس الأصل: Stale-While-Revalidate (نرجّع الكاش فورًا ونحدّثه بالخلفية) */
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);
  if (url.origin !== location.origin) return;
  if (url.pathname === "/sw.js") return; // ما نتدخلش في ملف الـ SW نفسه

  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(OFFLINE_URL))
    );
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

/* تحديث فوري عند رسالة SKIP_WAITING */
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") self.skipWaiting();
});

