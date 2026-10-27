// Lamp's service worker: keeps the app and every Bible you've opened on the phone, so Lamp works offline.
// build.py fills in the two versions from the files' contents.
const SHELL = "lamp-shell-__SHELL_VERSION__";   // the app page, manifest and icons
const DATA = "lamp-data-__DATA_VERSION__";      // Bibles, cross-references and dictionary (large, so only fetched when used)
const FONTS = "lamp-fonts";
const SHELL_FILES = ["./", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png",
  "icons/icon-maskable-512.png", "icons/apple-touch-icon.png", "icons/favicon-32.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  const keep = [SHELL, DATA, FONTS];
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith("lamp-") && !keep.includes(k)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Look in the cache first; otherwise fetch and keep a copy.
async function cacheFirst(cacheName, request, key = request) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(key);
  if (hit) return hit;
  const res = await fetch(request);
  if (res.ok || res.type === "opaque") cache.put(key, res.clone());
  return res;
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (req.mode === "navigate" && url.origin === location.origin) {
    // Every page of the app is the same document.
    e.respondWith(cacheFirst(SHELL, req, new URL("./", location.href).href).catch(() => caches.match("./")));
  } else if (url.origin === location.origin && url.pathname.endsWith(".json")) {
    e.respondWith(cacheFirst(DATA, req));
  } else if (url.origin === location.origin) {
    e.respondWith(cacheFirst(SHELL, req));
  } else if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(cacheFirst(FONTS, req));
  }
  // Anything else (Google Calendar links and so on) goes straight to the network.
});
