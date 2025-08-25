const CACHE_NAME = 'erp-mobile-cache-v1';
const OFFLINE_URL = '/mobile/';
const STATIC_ASSETS = [
  '/',
  OFFLINE_URL,
  '/static/mobile/manifest.json',
  '/static/mobile/icons/icon-192x192.png',
  '/static/mobile/icons/icon-512x512.png',
];

// تثبيت الـ Service Worker وتخزين الملفات الأساسية
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// تفعيل التحديث
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// التعامل مع الطلبات
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        const cloned = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, cloned);
        });
        return response;
      })
      .catch(() => caches.match(event.request).then(resp => resp || caches.match(OFFLINE_URL)))
  );
});
