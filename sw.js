const CACHE = 'cw-practice-v70';
const AUDIO_CACHE = 'cw-audio';   // stable name — survives SW version bumps
const ASSETS = [
  './CW_words_practice.html',
  './manifest.json',
  './audio/manifest.json',
  './icons/icon.svg',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE && k !== AUDIO_CACHE).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('message', e => {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;

  // Navigation requests (page loads): look up the HTML by its known cache key
  // rather than the request URL. This avoids URL mismatches (IP change, port
  // change, trailing slash) that cause caches.match(request) to return null,
  // which then falls through to network — which fails when offline.
  if (e.request.mode === 'navigate') {
    e.respondWith(
      caches.match('./CW_words_practice.html')
        .then(cached => cached || fetch(e.request).then(res => {
          if (res.ok) caches.open(CACHE).then(c => c.put('./CW_words_practice.html', res.clone()));
          return res;
        }))
        .catch(() => caches.match('./CW_words_practice.html'))
    );
    return;
  }

  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).then(res => {
      if (res.ok) {
        const clone = res.clone();
        const isAudio = e.request.url.includes('/audio/words/');
        caches.open(isAudio ? AUDIO_CACHE : CACHE).then(c => c.put(e.request, clone));
      }
      return res;
    }))
  );
});
