const { escapeHtml, buildFooterText, formatTimestamp, getFavorites, toggleFavorite, isFavorite } = require('../assets/shared.js');

describe('shared utilities', () => {
    it('escapes HTML-sensitive characters', () => {
        expect(escapeHtml('<script>"x"&\'y\'</script>')).toBe('&lt;script&gt;&quot;x&quot;&amp;&#39;y&#39;&lt;/script&gt;');
    });

    it('formats timestamp in UTC format', () => {
        const ts = new Date('2026-04-20T13:59:05.000Z');
        expect(formatTimestamp(ts)).toBe('2026-04-20 13:59:05 UTC');
    });

    it('builds footer text with timestamp', () => {
        const ts = new Date('2026-04-20T13:59:05.000Z');
        const html = buildFooterText(2026, ts);
        expect(html).toContain('2026 MLB Season');
        expect(html).toContain('Data from MLB Stats API');
        expect(html).toContain('Last updated: 2026-04-20 13:59:05 UTC');
    });

    it('builds footer fallback text when timestamp missing', () => {
        expect(buildFooterText(2026, null)).toContain('Last updated: Waiting for data');
    });
});

describe('favorites utilities', () => {
    let store;

    beforeEach(() => {
        store = {};
        global.localStorage = {
            getItem: (key) => (key in store ? store[key] : null),
            setItem: (key, val) => { store[key] = String(val); }
        };
    });

    afterEach(() => {
        delete global.localStorage;
    });

    it('getFavorites returns default structure when nothing stored', () => {
        expect(getFavorites()).toEqual({ teams: [], players: [] });
    });

    it('getFavorites returns stored favorites', () => {
        store.mlbFavorites = JSON.stringify({ teams: [{ id: '110', name: 'Baltimore Orioles' }], players: [] });
        expect(getFavorites().teams).toEqual([{ id: '110', name: 'Baltimore Orioles' }]);
    });

    it('toggleFavorite adds a team and returns true', () => {
        const result = toggleFavorite('teams', '110', 'Baltimore Orioles');
        expect(result).toBe(true);
        expect(getFavorites().teams).toEqual([{ id: '110', name: 'Baltimore Orioles' }]);
    });

    it('toggleFavorite removes a team when already favorited and returns false', () => {
        toggleFavorite('teams', '110', 'Baltimore Orioles');
        const result = toggleFavorite('teams', '110', 'Baltimore Orioles');
        expect(result).toBe(false);
        expect(getFavorites().teams).toEqual([]);
    });

    it('toggleFavorite adds a player', () => {
        toggleFavorite('players', '592450', 'Mike Trout');
        expect(getFavorites().players).toEqual([{ id: '592450', name: 'Mike Trout' }]);
    });

    it('isFavorite returns true for a favorited team', () => {
        toggleFavorite('teams', '110', 'Baltimore Orioles');
        expect(isFavorite('teams', '110')).toBe(true);
    });

    it('isFavorite returns false for a non-favorited item', () => {
        expect(isFavorite('players', '99999')).toBe(false);
    });

    it('isFavorite coerces id to string for comparison', () => {
        toggleFavorite('teams', 110, 'Baltimore Orioles');
        expect(isFavorite('teams', '110')).toBe(true);
    });
});

