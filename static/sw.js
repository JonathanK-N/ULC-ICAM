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

// Gestion des notifications push
self.addEventListener('push', event => {
  console.log('[SW] Push reçu:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Nouvelle notification ULC-ICAM',
    icon: '/static/images/pwa-icon-192.png',
    badge: '/static/images/pwa-icon-192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Voir',
        icon: '/static/images/pwa-icon-192.png'
      },
      {
        action: 'close',
        title: 'Fermer',
        icon: '/static/images/pwa-icon-192.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('ULC-ICAM Turnin', options)
  );
});

// Gestion des clics sur notifications
self.addEventListener('notificationclick', event => {
  console.log('[SW] Clic notification:', event);
  
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  } else if (event.action === 'close') {
    // Fermer la notification
  } else {
    // Clic par défaut
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});
