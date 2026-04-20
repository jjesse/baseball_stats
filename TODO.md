# MLB Web App — TODO

> Last reviewed: 2026-04-20

## ✅ Completed

- [x] Make player names clickable for detailed player profiles — `player.html` + `player.js` fully implemented with bio, career stats, season stats, and splits tabs
- [x] Add recent results and upcoming games to team pages — `fetchTeamSchedule()` in `team.js` shows last 7 days of results and next 7 days of games
- [x] Allow sorting/filtering of leaderboards and standings by any column — `currentSort` logic in `app.js`; batting/pitching leaders use tabbed views
- [x] Add a global search bar to find teams or players by name — `search.html` + `search.js` with live API search, plus a nav search bar on every page
- [x] Add today's live scores/scoreboard as a homepage section or dedicated page — `scoreboard.html` + `scoreboard.js` with date navigation and live game cards
- [x] Add team schedule to team pages (upcoming and recent games) — implemented via `fetchTeamSchedule()` in `team.js`
- [x] Add per-player stats (batting/pitching) on the team roster page — `fetchRosterStats()` in `team.js` fetches and renders hitting/pitching stats inline in the roster
- [x] Add career stats and splits on player profile pages — `fetchCareerStats()` and `fetchSplits()` in `player.js`
- [x] Show user-friendly error messages for API failures — `.no-data-message` divs with ⚠️ messages used throughout all JS files
- [x] Further optimize tables and layout for mobile devices — `@media (max-width: 600px)` styles in `assets/styles.css`

---

## 🔴 High Priority

- [ ] **Fix CSS syntax bug in `archives/2025/assets/styles.css`** — the `body {}` block is missing its closing `}`, causing `.header-row`, `.nav-links`, and related rules to be incorrectly nested inside it (around lines 41–64)
- [ ] Extract shared utilities (`escapeHtml`, dark mode toggle, footer setter) into a single shared module — the same code is duplicated across `app.js`, `batting.js`, `pitching.js`, `team.js`, `search.js`, and `player.js`
- [ ] Add data freshness timestamp in the footer — currently all pages say "Updated live" but never show when data was last fetched; replace with the actual fetch timestamp
- [ ] Add ESLint to CI for consistent code style enforcement — currently CI only runs `node --check` (syntax only) and `html-validate`
- [ ] Add unit tests for JavaScript functions (e.g., with Jest or Vitest) — CI currently only does syntax checks, not behavioral tests
- [ ] Add CI/CD deployment automation (e.g., GitHub Pages deploy on merge to main) — CI currently only validates; it does not deploy
- [ ] Handle API rate limiting gracefully (retry, backoff, cache) — no retry/backoff logic exists; repeated failed fetches have no protection
- [ ] Improve accessibility (ARIA labels, color contrast, keyboard navigation) — only the nav search bar has `aria-label`; tables, buttons, and tabs lack proper ARIA roles and keyboard support

---

## 🟡 Medium Priority

- [ ] Add loading indicators (spinners/progress bars) while data loads — pages currently show a plain "Loading…" text node; no visual spinner or progress bar
- [ ] Enable selection of previous seasons for standings and leaders — currently the app always uses the current year; no season picker exists
- [ ] Add more years to the archive system — only the 2025 season is archived; automate archiving or add a season dropdown to the main pages
- [ ] Modularize JavaScript (ES modules or a lightweight bundler) — all JS files are standalone globals; switching to ES modules would enable proper imports and reduce duplication
- [ ] Add meta tags and improve SEO — HTML pages lack `<meta name="description">`, Open Graph tags, and canonical URLs
- [ ] Add advanced stats (WAR, wOBA, FIP, etc.) on batting/pitching leaderboards and player pages
- [ ] Add charts/visualizations for trends, comparisons, and playoff odds (e.g., using Chart.js)
- [ ] Add end-to-end tests (e.g., Playwright or Cypress) to verify data renders correctly in the browser
- [ ] Run Lighthouse CI in the workflow to track performance, accessibility, and SEO scores over time
- [ ] Add print stylesheet (`@media print`) so standings/stats pages print cleanly

---

## 🟢 Low Priority

- [ ] Add playoff picture/bracket visualization (e.g., Wild Card race leaders, projected matchups)
- [ ] Add player-vs-player comparison tool (side-by-side career/season stats)
- [ ] Let users favorite/star teams or players (persisted in `localStorage`)
- [ ] Add PWA support (installable, offline basic features via a Service Worker)
- [ ] Add a Content Security Policy header if the app is self-hosted, to restrict external script/data sources
- [ ] Integrate MLB news or team/player headlines
- [ ] Add social sharing buttons for teams, players, and leaderboards
- [ ] Support multiple languages and time zones (localization / `Intl` API)
- [ ] Add CSV/JSON export buttons on standings and leader tables so users can download data
- [ ] Add game alerts or notifications (browser Push API or email) for tracked teams' game results
