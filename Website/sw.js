const CACHE_NAME = 'chegu-portfolio-v2';

self.addEventListener('install', event => {
    self.skipWaiting(); // Force the waiting service worker to become the active service worker
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll([
                './',
                './index.html',
                './css/style.css',
                './js/main.js'
            ]);
        })
    );
});

self.addEventListener('activate', event => {
    // Delete old caches
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim(); // Take control of all pages immediately
});

self.addEventListener('fetch', event => {
    // Network First strategy
    event.respondWith(
        fetch(event.request).then(response => {
            // If network request succeeds, update the cache
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, responseClone);
            });
            return response;
        }).catch(() => {
            // If network fails (offline), use the cache
            return caches.match(event.request);
        })
    );
});
