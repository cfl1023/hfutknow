const CACHE = 'hfutknow-v8';
const ASSETS = ['./', './index.html', './style.css', './app.js', './manifest.webmanifest', './assets/icon-192.png', './forum.html', './forum.js', './discuss-home.js'];

// 网络优先：在线时永远拿最新数据，离线时才回退缓存。
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()).catch(() => {})
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request)
      .then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((c) => c.put(event.request, copy)).catch(() => {});
        return resp;
      })
      .catch(() => {
        if (event.request.mode === 'navigate') {
          const u = new URL(event.request.url);
          if (/forum\.html$/.test(u.pathname)) {
            return caches.match('./forum.html').then((r) => r || caches.match('./index.html'));
          }
          return caches.match('./index.html');
        }
        return caches.match(event.request);
      })
  );
});
