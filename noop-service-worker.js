self.addEventListener('install', () => {
  return self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  return self.clients.claim();
});
