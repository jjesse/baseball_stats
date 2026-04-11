// Shared utilities for the MLB Stats web app

// Simple in-memory cache with TTL to handle API rate limiting
const apiCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function fetchWithRetry(url, maxRetries = 3) {
    const cached = apiCache.get(url);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data;
    }
    let lastError;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const res = await fetch(url);
            if (res.status === 429) {
                const waitMs = Math.pow(2, attempt) * 1000;
                await new Promise(r => setTimeout(r, waitMs));
                continue;
            }
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            apiCache.set(url, { data, timestamp: Date.now() });
            return data;
        } catch (e) {
            lastError = e;
            if (attempt < maxRetries - 1) {
                await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000));
            }
        }
    }
    throw lastError;
}

function updateFooterTimestamp(currentYear) {
    const footer = document.getElementById('footer');
    if (footer) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        footer.innerHTML = `${currentYear} MLB Season &middot; Data from MLB Stats API &middot; Last updated: ${timeStr}`;
    }
}
