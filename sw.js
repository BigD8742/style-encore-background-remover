// Keeps a copy of the AI files on the phone after the first download, so the app starts quickly
// every time instead of downloading about 90 MB again. Only the AI library and model files are kept;
// they have version numbers in their web addresses, so a stored copy never goes out of date.
// The app page itself is always loaded fresh, so updates still arrive normally.
const CACHE = "ai-files-v1";
const AI_HOSTS = ["staticimgly.com", "cdn.jsdelivr.net"];

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) if (name !== CACHE) await caches.delete(name);
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || !AI_HOSTS.some((h) => url.hostname === h || url.hostname.endsWith("." + h))) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req, { ignoreVary: true });
    if (hit) return hit;
    const res = await fetch(req);
    if (res.ok && res.type !== "opaque") cache.put(req, res.clone()).catch(() => { /* phone storage full: just skip */ });
    return res;
  })());
});
