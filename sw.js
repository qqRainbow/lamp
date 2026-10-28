// Lamp's service worker: keeps the app and every Bible you've opened on the phone, so Lamp works offline.
// build.py fills in the two versions from the files' contents.
const SHELL = "lamp-shell-__SHELL_VERSION__";   // the app page, manifest, icons and fonts
const DATA = "lamp-data-__DATA_VERSION__";      // Bibles, cross-references and dictionary (large, so only fetched when used)
const SHELL_FILES = ["./", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png",
  "icons/icon-maskable-512.png", "icons/apple-touch-icon.png", "icons/favicon-32.png", __FONT_FILES__];
const PAGE_WAIT = 3000;  // how long opening Lamp waits for the newest page before using the saved one

self.addEventListener("install", e => {
  // "reload" skips the browser's own cache (GitHub lets it keep files 10 minutes), so a new version saves new files.
  e.waitUntil(caches.open(SHELL)
    .then(c => c.addAll(SHELL_FILES.map(f => new Request(f, { cache: "reload" }))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  const keep = [SHELL, DATA];  // also clears the old Google Fonts cache, "lamp-fonts"
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

// The app page: the newest from the internet when it answers quickly, otherwise the saved copy (offline, or a slow connection).
// "no-cache" asks GitHub whether the page changed, which is a tiny request when it hasn't.
async function newestPage() {
  const cache = await caches.open(SHELL), key = new URL("./", location.href).href;
  try {
    const res = await Promise.race([
      fetch(key, { cache: "no-cache", credentials: "same-origin" }),
      new Promise((_, fail) => setTimeout(() => fail(new Error("slow")), PAGE_WAIT)),
    ]);
    if (res.ok) { await cache.put(key, res.clone()); return res; }
  } catch {}
  return (await cache.match(key)) || fetch(key);
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (req.mode === "navigate" && url.origin === location.origin) {
    // Every page of the app is the same document.
    e.respondWith(newestPage());
  } else if (url.origin === location.origin && url.pathname.endsWith(".json")) {
    e.respondWith(cacheFirst(DATA, req));
  } else if (url.origin === location.origin) {
    e.respondWith(cacheFirst(SHELL, req));
  }
  // Anything else (Google Calendar links and so on) goes straight to the network.
});
