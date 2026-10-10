// ULC-ICAM PWA Service Worker
// © 2024 Cognito Inc. - Tous droits réservés
const CACHE_NAME = 'ulc-icam-public-v2';
const OFFLINE_URL = '/offline.html';
const STATIC_CACHE_URLS = [
  OFFLINE_URL,
  '/static/images/pwa-icon-192.png',
  '/static/images/pwa-icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME)
    .then(cache => cache.addAll(STATIC_CACHE_URLS))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(names => Promise.all(
    names.filter(name => name.startsWith('ulc-icam-') && name !== CACHE_NAME)
      .map(name => caches.delete(name))
  )).then(() => self.clients.claim()));
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) return;
  // Only a fixed public allowlist may be cached. Every authenticated route stays online.
  if (STATIC_CACHE_URLS.includes(url.pathname) && !url.search) {
    event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request)));
    return;
  }
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).catch(() => caches.match(OFFLINE_URL)));
  }
});

// Notifications remain generic on the lock screen.
self.addEventListener('push', event => {
  let payload = {};
  try { payload = event.data ? event.data.json() : {}; } catch (_) {}
  event.waitUntil(self.registration.showNotification('Cognito Web', {
    body: 'Une nouvelle information est disponible dans votre espace.',
    icon: '/static/images/pwa-icon-192.png', badge: '/static/images/pwa-icon-192.png',
    tag: String(payload.tag || 'cognito-notification').slice(0, 80),
    data: { url: '/notifications' }
  }));
});
self.addEventListener('notificationclick', event => {
  event.notification.close();
  const destination = new URL(event.notification.data?.url || '/notifications', self.location.origin);
  const safeUrl = destination.origin === self.location.origin ? destination.href : self.location.origin + '/notifications';
  event.waitUntil(clients.openWindow(safeUrl));
});
