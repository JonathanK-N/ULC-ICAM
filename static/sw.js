// ULC-ICAM PWA Service Worker
// © 2024 Cognito Inc. - Tous droits réservés

const CACHE_NAME = 'ulc-icam-v1.0.0';
const OFFLINE_URL = '/offline.html';

const STATIC_CACHE_URLS = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/images/ulc-icam-logo.png',
  '/static/images/ulc-icam-logo-192.png',
  '/static/images/ulc-icam-logo-512.png',
  '/static/manifest.json',
  OFFLINE_URL
];

const DYNAMIC_CACHE_URLS = [
  '/dashboard',
  '/login',
  '/student/my_grades',
  '/teacher/assignments'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  console.log('[SW] Installation...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Cache ouvert');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activation du Service Worker
self.addEventListener('activate', event => {
  console.log('[SW] Activation...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Suppression ancien cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Interception des requêtes
self.addEventListener('fetch', event => {
  // Ignorer les requêtes non-GET
  if (event.request.method !== 'GET') return;
  
  // Ignorer les requêtes externes
  if (!event.request.url.startsWith(self.location.origin)) return;

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Retourner depuis le cache si disponible
        if (response) {
          console.log('[SW] Depuis cache:', event.request.url);
          return response;
        }

        // Sinon, faire la requête réseau
        return fetch(event.request)
          .then(response => {
            // Vérifier si la réponse est valide
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Cloner la réponse pour le cache
            const responseToCache = response.clone();

            // Mettre en cache les pages importantes
            if (DYNAMIC_CACHE_URLS.some(url => event.request.url.includes(url))) {
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }

            return response;
          })
          .catch(() => {
            // En cas d'erreur réseau, retourner la page offline
            if (event.request.destination === 'document') {
              return caches.match(OFFLINE_URL);
            }
          });
      })
  );
});

// Gestion des notifications push
self.addEventListener('push', event => {
  console.log('[SW] Push reçu:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Nouvelle notification ULC-ICAM',
    icon: '/static/images/ulc-icam-logo-192.png',
    badge: '/static/images/ulc-icam-logo-192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Voir',
        icon: '/static/images/ulc-icam-logo-192.png'
      },
      {
        action: 'close',
        title: 'Fermer',
        icon: '/static/images/ulc-icam-logo-192.png'
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

// Synchronisation en arrière-plan
self.addEventListener('sync', event => {
  console.log('[SW] Sync:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Synchroniser les données en attente
      syncPendingData()
    );
  }
});

async function syncPendingData() {
  try {
    // Récupérer les données en attente depuis IndexedDB
    const pendingData = await getPendingSubmissions();
    
    for (const data of pendingData) {
      try {
        await fetch('/api/sync', {
          method: 'POST',
          body: JSON.stringify(data),
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        // Supprimer de la file d'attente après succès
        await removePendingSubmission(data.id);
      } catch (error) {
        console.log('[SW] Erreur sync:', error);
      }
    }
  } catch (error) {
    console.log('[SW] Erreur sync générale:', error);
  }
}

// Fonctions utilitaires pour IndexedDB (simplifiées)
async function getPendingSubmissions() {
  // Implémentation simplifiée
  return [];
}

async function removePendingSubmission(id) {
  // Implémentation simplifiée
  console.log('[SW] Suppression soumission:', id);
}
