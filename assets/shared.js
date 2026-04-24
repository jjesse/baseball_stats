(function (root, factory) {
    if (typeof module === 'object' && module.exports) {
        module.exports = factory();
        return;
    }
    root.MLBUtils = factory();
})(typeof globalThis !== 'undefined' ? globalThis : (typeof self !== 'undefined' ? self : this), function () {
    const responseCache = new Map();

    function escapeHtml(value) {
        if (value === null || value === undefined) return '';
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatTimestamp(date) {
        if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
            return 'Unknown';
        }
        return date.toISOString().replace('T', ' ').replace('.000Z', ' UTC');
    }

    function buildFooterText(year, timestamp) {
        const stamp = timestamp ? formatTimestamp(timestamp) : 'Waiting for data';
        return `${year} MLB Season · Data from MLB Stats API · Last updated: ${stamp}`;
    }

    function createFooterUpdater(year, footerId = 'footer') {
        const footer = typeof document !== 'undefined' ? document.getElementById(footerId) : null;
        let latestTimestamp = 0;

        if (footer) {
            footer.textContent = buildFooterText(year, null);
        }

        return function updateFooter(timestamp = new Date()) {
            if (!footer) return;
            const ts = timestamp instanceof Date ? timestamp.getTime() : new Date(timestamp).getTime();
            if (Number.isNaN(ts) || ts < latestTimestamp) return;
            latestTimestamp = ts;
            footer.textContent = buildFooterText(year, new Date(ts));
        };
    }

    function initDarkModeToggle(toggleId = 'darkModeToggle', storageKey = 'mlbDarkMode') {
        if (typeof document === 'undefined') return;
        const darkModeToggle = document.getElementById(toggleId);
        if (!darkModeToggle) return;

        const applyDarkMode = (enabled) => {
            document.body.classList.toggle('dark', enabled);
            darkModeToggle.setAttribute('aria-pressed', enabled ? 'true' : 'false');
        };

        applyDarkMode(localStorage.getItem(storageKey) === 'true');

        darkModeToggle.onclick = function () {
            const isDark = !document.body.classList.contains('dark');
            applyDarkMode(isDark);
            localStorage.setItem(storageKey, isDark ? 'true' : 'false');
        };
    }

    function sleep(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    async function fetchJsonWithRetry(url, options = {}) {
        const retries = Number.isInteger(options.retries) ? options.retries : 2;
        const retryDelayMs = Number.isInteger(options.retryDelayMs) ? options.retryDelayMs : 400;
        const cacheTtlMs = Number.isInteger(options.cacheTtlMs) ? options.cacheTtlMs : 0;

        if (cacheTtlMs > 0) {
            const cached = responseCache.get(url);
            if (cached && Date.now() - cached.timestamp <= cacheTtlMs) {
                return cached.value;
            }
        }

        let lastError;
        for (let attempt = 0; attempt <= retries; attempt += 1) {
            try {
                const res = await fetch(url);
                if (res.status === 429 || res.status >= 500) {
                    if (attempt < retries) {
                        await sleep(retryDelayMs * (2 ** attempt));
                        continue;
                    }
                }
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                if (cacheTtlMs > 0) {
                    responseCache.set(url, { timestamp: Date.now(), value: data });
                }
                return data;
            } catch (error) {
                lastError = error;
                if (attempt < retries) {
                    await sleep(retryDelayMs * (2 ** attempt));
                    continue;
                }
            }
        }
        throw lastError || new Error('Request failed');
    }

    function setupAccessibleTabs(config) {
        if (typeof document === 'undefined') return;
        const tabButtons = Array.from(document.querySelectorAll(config.tabSelector));
        if (tabButtons.length === 0) return;

        const tabList = tabButtons[0].closest('.tabs');
        if (tabList) tabList.setAttribute('role', 'tablist');

        const activate = (btn) => {
            tabButtons.forEach((button) => {
                const panelId = `${config.panelPrefix}${button.dataset.tab}`;
                const panel = document.getElementById(panelId);
                const isActive = button === btn;
                button.classList.toggle('active', isActive);
                button.setAttribute('aria-selected', isActive ? 'true' : 'false');
                button.setAttribute('tabindex', isActive ? '0' : '-1');
                if (panel) {
                    panel.classList.toggle('active', isActive);
                    panel.hidden = !isActive;
                }
            });
        };

        tabButtons.forEach((btn, index) => {
            const panelId = `${config.panelPrefix}${btn.dataset.tab}`;
            const panel = document.getElementById(panelId);
            if (!btn.id) btn.id = `${config.idPrefix || 'tab'}-${btn.dataset.tab}`;

            btn.setAttribute('role', 'tab');
            btn.setAttribute('aria-controls', panelId);
            btn.setAttribute('aria-selected', btn.classList.contains('active') ? 'true' : 'false');
            btn.setAttribute('tabindex', btn.classList.contains('active') ? '0' : '-1');

            if (panel) {
                panel.setAttribute('role', 'tabpanel');
                panel.setAttribute('aria-labelledby', btn.id);
                panel.hidden = !btn.classList.contains('active');
            }

            btn.onclick = () => activate(btn);
            btn.addEventListener('keydown', (event) => {
                const key = event.key;
                let targetIndex = index;
                if (key === 'ArrowRight') targetIndex = (index + 1) % tabButtons.length;
                if (key === 'ArrowLeft') targetIndex = (index - 1 + tabButtons.length) % tabButtons.length;
                if (key === 'Home') targetIndex = 0;
                if (key === 'End') targetIndex = tabButtons.length - 1;

                if (targetIndex !== index) {
                    event.preventDefault();
                    tabButtons[targetIndex].focus();
                    activate(tabButtons[targetIndex]);
                }
            });
        });
    }

    function getFavorites() {
        if (typeof localStorage === 'undefined') return { teams: [], players: [] };
        try {
            const raw = localStorage.getItem('mlbFavorites');
            const parsed = raw ? JSON.parse(raw) : {};
            return {
                teams: Array.isArray(parsed.teams) ? parsed.teams : [],
                players: Array.isArray(parsed.players) ? parsed.players : []
            };
        } catch (e) {
            return { teams: [], players: [] };
        }
    }

    function toggleFavorite(type, id, name) {
        if (typeof localStorage === 'undefined') return false;
        const favs = getFavorites();
        if (!Array.isArray(favs[type])) favs[type] = [];
        const sid = String(id);
        const idx = favs[type].findIndex((item) => String(item.id) === sid);
        let nowFavorited;
        if (idx >= 0) {
            favs[type].splice(idx, 1);
            nowFavorited = false;
        } else {
            favs[type].push({ id: sid, name: String(name) });
            nowFavorited = true;
        }
        try {
            localStorage.setItem('mlbFavorites', JSON.stringify(favs));
        } catch (e) { /* quota exceeded or private browsing */ }
        return nowFavorited;
    }

    function isFavorite(type, id) {
        const favs = getFavorites();
        const list = Array.isArray(favs[type]) ? favs[type] : [];
        const sid = String(id);
        return list.some((item) => String(item.id) === sid);
    }

    function exportSectionToCsv(containerEl, filename) {
        if (typeof document === 'undefined' || typeof URL === 'undefined' || !URL.createObjectURL) return;
        const lines = [];
        containerEl.querySelectorAll('h2, h3, table').forEach((el) => {
            if (el.tagName === 'H2' || el.tagName === 'H3') {
                if (lines.length > 0) lines.push('');
                lines.push(el.textContent.trim());
            } else {
                el.querySelectorAll('tr').forEach((row) => {
                    const cols = Array.from(row.querySelectorAll('th, td'))
                        .map((cell) => `"${cell.textContent.trim().replace(/"/g, '""')}"`);
                    if (cols.length > 0) lines.push(cols.join(','));
                });
            }
        });
        if (lines.length === 0) return;
        const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
    }

    function makeSortableHeadersAccessible(selector, onActivate, getSortState) {
        if (typeof document === 'undefined') return;
        document.querySelectorAll(selector).forEach((th) => {
            th.setAttribute('role', 'button');
            th.setAttribute('tabindex', '0');
            th.setAttribute('aria-label', `${th.textContent.trim()} sortable column`);

            const applyAriaSort = () => {
                const state = getSortState ? getSortState(th) : null;
                th.setAttribute('aria-sort', state || 'none');
            };

            const activate = () => {
                onActivate(th);
                applyAriaSort();
            };

            th.onclick = activate;
            th.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    activate();
                }
            });

            applyAriaSort();
        });
    }

    return {
        buildFooterText,
        createFooterUpdater,
        escapeHtml,
        exportSectionToCsv,
        fetchJsonWithRetry,
        formatTimestamp,
        getFavorites,
        initDarkModeToggle,
        isFavorite,
        makeSortableHeadersAccessible,
        setupAccessibleTabs,
        toggleFavorite
    };
});
