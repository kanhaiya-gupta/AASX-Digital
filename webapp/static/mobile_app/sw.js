// AASX Digital Twin Analytics - Service Worker
const CACHE_NAME = 'aasx-digital-v1.0.0';
const STATIC_CACHE = 'aasx-static-v1.0.0';
const DYNAMIC_CACHE = 'aasx-dynamic-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
  '/',
  '/dashboard',
  '/twin-registry',
  '/ai-rag',
  '/certificates',
  '/federated-learning',
  '/physics-modeling',
  '/mobile_app/pwa/manifest.json',
  '/mobile_app/pwa/sw.js'
];

// API endpoints to cache
const API_CACHE = [
  '/api/health',
  '/api/dashboard',
  '/api/twin-registry',
  '/api/ai-rag',
  '/api/certificate-manager',
  '/api/federated-learning',
  '/api/physics-modeling'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
  console.log('🔄 Service Worker: Installing...');
  
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE)
        .then((cache) => {
          console.log('📦 Caching static files');
          return cache.addAll(STATIC_FILES);
        }),
      caches.open(DYNAMIC_CACHE)
        .then((cache) => {
          console.log('📦 Caching API endpoints');
          return cache.addAll(API_CACHE);
        })
    ])
  );
  
  // Skip waiting to activate immediately
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  // Claim all clients
  self.clients.claim();
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // Handle static files
  if (url.pathname.startsWith('/mobile_app/') || 
      url.pathname.startsWith('/static/') ||
      url.pathname === '/' ||
      url.pathname.startsWith('/dashboard') ||
      url.pathname.startsWith('/twin-registry') ||
      url.pathname.startsWith('/ai-rag') ||
      url.pathname.startsWith('/certificates') ||
      url.pathname.startsWith('/federated-learning') ||
      url.pathname.startsWith('/physics-modeling')) {
    
    event.respondWith(handleStaticRequest(request));
    return;
  }
  
  // For other requests, try network first
  event.respondWith(
    fetch(request)
      .catch(() => {
        return caches.match(request);
      })
  );
});

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('📡 Network failed, trying cache for:', request.url);
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for API requests
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'Please check your internet connection' 
      }),
      { 
        status: 503, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }
}

// Handle static requests with cache-first strategy
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('📡 Network failed for static file:', request.url);
    
    // Return offline page
    return caches.match('/offline.html') || 
           new Response('Offline - Please check your connection', { status: 503 });
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('🔄 Background sync triggered');
    event.waitUntil(doBackgroundSync());
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  console.log('📱 Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New update available',
    icon: '/mobile_app/pwa/icons/icon-192x192.png',
    badge: '/mobile_app/pwa/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View',
        icon: '/mobile_app/pwa/icons/icon-72x72.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/mobile_app/pwa/icons/icon-72x72.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('AASX Digital Twin Analytics', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('📱 Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});

// Background sync function
async function doBackgroundSync() {
  try {
    // Sync any pending data
    console.log('🔄 Performing background sync');
    
    // You can add specific sync logic here
    // For example, sync offline form submissions
    
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}
