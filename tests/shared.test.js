const { describe, it, expect } = require('vitest');
const { escapeHtml, buildFooterText, formatTimestamp } = require('../assets/shared.js');

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
