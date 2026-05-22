/// <reference lib="webworker" />
const sw = self;
const CACHE_NAME = "booklib-cache-v1.9.1"; // x-release-please-version
const URLS_TO_CACHE = [
    "/",
    "/manifest.json",
    "/static/css/main.css",
    "/static/js/main.js",
    "/static/js/views/Home.js",
    "/static/js/components/Navbar.js",
    "/static/js/components/BookCard.js",
    "/static/js/components/AddBookForm.js",
    "/static/js/components/EditBookModal.js",
    "/static/js/components/DetailModal.js",
    "/static/js/components/FilterPanel.js",
    "/static/js/components/GoogleBooksModal.js",
    "/static/js/components/BookSearchResult.js",
    "/static/js/utils/formatters.js",
    "/static/js/utils/theme.js",
    "/static/js/utils/useBodyScrollLock.js",
    "/static/js/services/api.js",
    "/static/covers/default.jpg",
    "/favicon.ico",
    "/static/icons/icon-48x48.png",
    "/static/icons/icon-72x72.png",
    "/static/icons/icon-96x96.png",
    "/static/icons/icon-128x128.png",
    "/static/icons/icon-144x144.png",
    "/static/icons/icon-152x152.png",
    "/static/icons/icon-192x192.png",
    "/static/icons/icon-256x256.png",
    "/static/icons/icon-384x384.png",
    "/static/icons/icon-512x512.png",
    "https://corsproxy.io/?url=https://cdn.tailwindcss.com",
    "https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js",
    "https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js",
];
sw.addEventListener("install", (event) => {
    console.log("[ServiceWorker] Installed");
    const precache = async () => {
        try {
            const cache = await caches.open(CACHE_NAME);
            console.log("[ServiceWorker] Main resources caching");
            const cachePromises = URLS_TO_CACHE.map(async (url) => {
                const request = new Request(url, { cache: "reload" });
                return cache.add(request).catch((err) => {
                    console.warn(`[ServiceWorker] Failed to cache ${url}:`, err);
                });
            });
            await Promise.all(cachePromises);
            await sw.skipWaiting();
        } catch (error) {
            console.error("[ServiceWorker] Pre-caching failed:", error);
        }
    };
    event.waitUntil(precache());
});
sw.addEventListener("activate", (event) => {
    console.log("[ServiceWorker] Activated");
    const cleanup = async () => {
        try {
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames
                    .filter((cacheName) => cacheName !== CACHE_NAME)
                    .map((cacheName) => {
                        console.log("[ServiceWorker] Removing old cache:", cacheName);
                        return caches.delete(cacheName);
                    })
            );
            await sw.clients.claim();
        } catch (error) {
            console.error("[ServiceWorker] Cache cleanup failed:", error);
        }
    };
    event.waitUntil(cleanup());
});
sw.addEventListener("fetch", (event) => {
    const { request } = event;
    if (request.method !== "GET") {
        return;
    }
    if (request.mode === "navigate" || request.url.includes("/books-data")) {
        event.respondWith(networkFirst(request));
        return;
    }
    event.respondWith(cacheFirst(request));
});
const fetchAndCache = async (request) => {
    const networkResponse = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
    return networkResponse;
};
const networkFirst = async (request) => {
    try {
        return await fetchAndCache(request);
    } catch (error) {
        console.warn("[ServiceWorker] Network failed, trying cache for:", request.url, error);
        const cachedResponse = await caches.match(request);
        return cachedResponse;
    }
};
const cacheFirst = async (request) => {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    try {
        return await fetchAndCache(request);
    } catch (error) {
        console.error("[ServiceWorker] Fetch failed, not in cache:", request.url, error);
    }
};
