# core/views_pwa.py
from django.http import HttpResponse
from django.utils.translation import get_language
from django.views.decorators.http import require_GET
from django.templatetags.static import static
from django.contrib.staticfiles import finders
import json

@require_GET
def manifest_json(request):
    lang = (get_language() or "ar").lower()
    is_ar = lang.startswith("ar")
    data = {
        "id": "/",
        "name": "نظام ERP الذكي" if is_ar else "ERP Smart System",
        "short_name": "ERP",
        "lang": "ar" if is_ar else "en",
        "dir": "rtl" if is_ar else "ltr",
        "start_url": "/?source=pwa",
        "scope": "/",
        "display": "standalone",
        "display_override": ["standalone", "fullscreen", "window-controls-overlay"],
        "background_color": "#121212",
        "theme_color": "#121212",
        "categories": ["business", "productivity"],
        "icons": [
            {"src": static("icons/icon-192x192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": static("icons/icon-512x512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
        "shortcuts": [
            {"name": ("لوحة التحكم" if is_ar else "Dashboard"), "url": "/dashboard/"},
            {"name": ("التطبيقات" if is_ar else "Apps"), "url": "/apps/"},
        ],
        "prefer_related_applications": False,
    }
    resp = HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/manifest+json; charset=utf-8")
    resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp["Pragma"] = "no-cache"
    resp["Expires"] = "0"
    return resp


def _read_static_sw_bytes() -> bytes | None:
    """
    نحاول قراءة ملف Service Worker الموحَّد من الستاتيك:
    يجرّب مسارات شائعة: sw.js ثم core/sw.js ثم core/static/sw.js
    """
    candidates = ("sw.js", "core/sw.js", "core/static/sw.js")
    for cand in candidates:
        path = finders.find(cand)
        if path:
            try:
                with open(path, "rb") as f:
                    return f.read()
            except Exception:
                continue
    return None


@require_GET
def service_worker(request):
    """
    توحيد SW على نسخة الستاتيك:
    - إن وُجد /static/.../sw.js نعيد محتواه عند المسار الجذري /sw.js.
    - إن لم يوجد، نعود لسلوكك الديناميكي السابق (بدون حذف أي ميزة).
    """
    content = _read_static_sw_bytes()
    if content:
        resp = HttpResponse(content, content_type="application/javascript; charset=utf-8")
        resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp["Pragma"] = "no-cache"
        resp["Expires"] = "0"
        resp["Service-Worker-Allowed"] = "/"
        return resp

    # ===== fallback: منطقك السابق كما هو (بدون حذف/تقليص) =====
    app_shell = [
        static("css/erp.css"),
        static("icons/icon-192x192.png"),
        static("icons/icon-512x512.png"),
        "/offline.html",
    ]
    js = f"""
    'use strict';
    const VERSION = 'erp-sw-v10';
    const STATIC_CACHE = VERSION + '-static';
    const RUNTIME_CACHE = VERSION + '-runtime';
    const APP_SHELL = {json.dumps(app_shell)};

    self.addEventListener('install', (event) => {{
      event.waitUntil(
        caches.open(STATIC_CACHE)
          .then((c) => c.addAll(APP_SHELL))
          .then(() => self.skipWaiting())
      );
    }});

    self.addEventListener('activate', (event) => {{
      event.waitUntil((async () => {{
        const keys = await caches.keys();
        await Promise.all(
          keys
            .filter((k) => ![STATIC_CACHE, RUNTIME_CACHE].includes(k))
            .map((k) => caches.delete(k))
        );
        if ('navigationPreload' in self.registration) {{
          try {{ await self.registration.navigationPreload.enable(); }} catch (e) {{}}
        }}
        await self.clients.claim();
      }})());
    }});

    function networkFirst(req, offlineFallback) {{
      return fetch(req, {{ cache: 'no-store' }})
        .then((res) => {{
          const clone = res.clone();
          caches.open(RUNTIME_CACHE).then((c) => c.put(req, clone));
          return res;
        }})
        .catch(() => offlineFallback ? caches.match(offlineFallback) : caches.match(req));
    }}

    function cacheFirst(req, targetCache) {{
      return caches.match(req).then((hit) => {{
        if (hit) return hit;
        return fetch(req).then((res) => {{
          const clone = res.clone();
          caches.open(targetCache).then((c) => c.put(req, clone));
          return res;
        }});
      }});
    }}

    function staleWhileRevalidate(req, targetCache) {{
      return caches.open(targetCache).then((cache) =>
        cache.match(req).then((cached) => {{
          const fetchPromise = fetch(req).then((res) => {{
            cache.put(req, res.clone());
            return res;
          }});
          return cached || fetchPromise;
        }})
      );
    }}

    self.addEventListener('fetch', (event) => {{
      const req = event.request;
      const url = new URL(req.url);

      // نهتم بطلبات GET من نفس الأصل فقط
      if (req.method !== 'GET' || url.origin !== self.location.origin) return;

      // استثناءات لا نتدخل بها
      if (
        url.pathname.startsWith('/set-language') ||
        url.pathname.startsWith('/i18n/') ||
        url.pathname.startsWith('/admin/') ||
        url.pathname.endsWith('.po') ||
        url.pathname.endsWith('.mo') ||
        url.pathname === '/sw.js'
      ) {{
        return;
      }}

      // تنقلات HTML: Network-First مع صفحة offline fallback
      if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {{
        event.respondWith(networkFirst(req, '/offline.html'));
        return;
      }}

      // ملفات الستاتيك: Stale-While-Revalidate
      if (url.pathname.startsWith('/static/')) {{
        event.respondWith(staleWhileRevalidate(req, STATIC_CACHE));
        return;
      }}

      // ملفات الميديا: Cache-First
      if (url.pathname.startsWith('/media/')) {{
        event.respondWith(cacheFirst(req, RUNTIME_CACHE));
        return;
      }}

      // باقي الطلبات: شبكة ثم كاش عند الفشل
      event.respondWith(fetch(req).catch(() => caches.match(req)));
    }});

    self.addEventListener('message', (event) => {{
      if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
    }});
    """
    resp = HttpResponse(js, content_type="application/javascript; charset=utf-8")
    resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp["Pragma"] = "no-cache"
    resp["Expires"] = "0"
    resp["Service-Worker-Allowed"] = "/"
    return resp
