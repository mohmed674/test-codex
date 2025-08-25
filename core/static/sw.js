/* ERP_CORE — Unified Service Worker (static) */
/* يحافظ على كل الميزات الموجودة ويضيف تحسينات دون حذف أي منطق */

/* ====== الإصدار / الكاش ====== */
const CACHE_PREFIX  = "erp-core-cache-";
const CACHE_VERSION = "v2025.08.22-01";
const CACHE_NAME    = `${CACHE_PREFIX}${CACHE_VERSION}`;
const OFFLINE_URL   = "/offline.html";

/* ====== ملفات تُخزَّن مسبقاً (ابقِ القائمة قابلة للزيادة) ====== */
const ASSETS_TO_CACHE = [
  "/",                         // الصفحة الرئيسية
  OFFLINE_URL,                 // صفحة العمل دون اتصال
  "/manifest.json",
  "/favicon.ico",
  "/static/css/erp.css",
  "/static/js/erp.js",
  "/static/js/main.js",
  "/static/icons/icon-192x192.png",
  "/static/icons/icon-512x512.png",
];

/* قناة اختيارية لإرسال رسائل للواجهة (لا تؤثر إن لم تُستخدم) */
let bc = null;
try { bc = new BroadcastChannel("erp-sw"); } catch (_) {}

/* ====== أدوات مساعدة ====== */
function sameOrigin(u) {
  try { return new URL(u, location.href).origin === location.origin; }
  catch (_) { return false; }
}
async function putSafe(request, response) {
  try {
    const c = await caches.open(CACHE_NAME);
    await c.put(request, response);
  } catch (_) {}
}

/* ====== التثبيت ====== */
self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await Promise.all(
      ASSETS_TO_CACHE.map(async (url) => {
        try {
          const resp = await fetch(url, { cache: "no-cache" });
          if (resp && resp.ok) await cache.put(url, resp.clone());
        } catch (_) { /* تجاهل العناصر المفقودة */ }
      })
    );
  })());
  self.skipWaiting();
});

/* ====== التفعيل ====== */
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    try {
      if (self.registration.navigationPreload) {
        await self.registration.navigationPreload.enable();
      }
    } catch (_) {}
    const keys = await caches.keys();
    await Promise.all(
      keys.map((k) =>
        (k === CACHE_NAME || !k.startsWith(CACHE_PREFIX)) ? null : caches.delete(k)
      )
    );
    await self.clients.claim();
    try { bc && bc.postMessage({ type: "SW_ACTIVATED", value: CACHE_NAME }); } catch (_) {}
  })());
});

/* ====== الاستراتيجيات ======
   - طلبات التنقل (navigate): شبكة أولاً + preload، ولو فشل -> offline.html
   - الأصول الثابتة (CSS/JS/صور) من نفس الأصل: Cache-first مع تحديث بالخلفية
   - باقي GET من نفس الأصل: Stale-While-Revalidate عامة
*/
self.addEventListener("fetch", (event) => {
  const { request } = event;

  // لا نتدخل في طلبات غير GET
  if (request.method !== "GET") return;

  const url = new URL(request.url);

  // لا نتدخل في SW نفسه (سواء /sw.js أو /static/sw.js)
  if (url.pathname === "/sw.js" || url.pathname === "/static/sw.js") return;

  // نسمح فقط بطلبات نفس الأصل
  if (!sameOrigin(url.href)) return;

  // تنقل صفحات HTML
  if (request.mode === "navigate") {
    event.respondWith((async () => {
      try {
        // استفد من Navigation Preload إن متاح
        const preload = await event.preloadResponse;
        if (preload) return preload;

        const net = await fetch(request);
        // يمكن تخزين الصفحة الرئيسية فقط (اختياري)
        return net;
      } catch (_) {
        const cached = await caches.match(OFFLINE_URL);
        return cached || Response.error();
      }
    })());
    return;
  }

  // أصول ثابتة من نفس الأصل
  if (/\.(?:css|js|png|svg|jpg|jpeg|webp|ico|woff2?|ttf|eot)$/i.test(url.pathname)) {
    event.respondWith((async () => {
      const cached = await caches.match(request);
      if (cached) {
        // حدّث بالخلفية بلا تعطيل
        event.waitUntil((async () => {
          try {
            const net = await fetch(request);
            if (net && net.ok) await putSafe(request, net.clone());
          } catch (_) {}
        })());
        return cached;
      }
      try {
        const net = await fetch(request);
        if (net && net.ok) await putSafe(request, net.clone());
        return net;
      } catch (_) {
        // حاول إرجاع أيقونة/ستايل بديل إن لزم
        return Response.error();
      }
    })());
    return;
  }

  // باقي GET: Stale-While-Revalidate
  event.respondWith((async () => {
    const cached = await caches.match(request);
    const netPromise = fetch(request)
      .then(async (net) => {
        if (net && net.ok) await putSafe(request, net.clone());
        return net;
      })
      .catch(() => cached);
    return cached || netPromise;
  })());
});

/* ====== الرسائل (Skip Waiting / Version) ====== */
self.addEventListener("message", (event) => {
  try {
    if (!event.data) return;
    if (event.data.type === "SKIP_WAITING") {
      self.skipWaiting();
    } else if (event.data.type === "GET_VERSION") {
      if (event.source && event.source.postMessage) {
        event.source.postMessage({ type: "SW_VERSION", value: CACHE_NAME });
      }
      try { bc && bc.postMessage({ type: "SW_VERSION", value: CACHE_NAME }); } catch (_) {}
    }
  } catch (_) {}
});

/* ====== Push/SYNC placeholders (اختيارية) ====== */
self.addEventListener("push", (e) => {
  if (!e.data) return;
  const payload = (() => { try { return e.data.json(); } catch (_) { return { title: "ERP", body: e.data.text() }; } })();
  e.waitUntil(
    self.registration.showNotification(payload.title || "ERP", {
      body: payload.body || "",
      icon: "/static/icons/icon-192x192.png",
      badge: "/static/icons/icon-192x192.png",
      data: payload.data || {},
    })
  );
});

self.addEventListener("sync", (e) => {
  // مثال: if (e.tag === "sync-outbox") { e.waitUntil(processOutbox()); }
});
