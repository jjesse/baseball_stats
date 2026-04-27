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

- [x] **Fix CSS syntax bug in `archives/2025/assets/styles.css`** — closed the missing `body {}` block so header/nav rules are no longer nested incorrectly
- [x] Extract shared utilities (`escapeHtml`, dark mode toggle, footer setter) into a single shared module — added `assets/shared.js` and refactored main scripts to consume it
- [x] Add data freshness timestamp in the footer — replaced “Updated live” with “Last updated” timestamps from successful API fetches
- [x] Add ESLint to CI for consistent code style enforcement — added ESLint config, npm scripts, and CI lint step
- [x] Add unit tests for JavaScript functions (e.g., with Jest or Vitest) — added Vitest tests for shared utilities and CI test step
- [x] Add CI/CD deployment automation (e.g., GitHub Pages deploy on merge to main) — added `.github/workflows/deploy.yml` for GitHub Pages deployment
- [x] Handle API rate limiting gracefully (retry, backoff, cache) — added `fetchJsonWithRetry` utility and adopted it across live-data pages
- [x] Improve accessibility (ARIA labels, color contrast, keyboard navigation) — added accessible tab semantics, keyboard-sortable headers, aria-live regions, and focus-visible styles

---

## 🟡 Medium Priority

- [x] Add loading indicators (spinners/progress bars) while data loads — added reusable spinner UI and replaced plain loading text on main pages and live loading states
- [x] Enable selection of previous seasons for standings and leaders — added season pickers on standings/batting/pitching pages with URL season persistence
- [ ] Add more years to the archive system — only the 2025 season is archived; automate archiving or add a season dropdown to the main pages
- [ ] Modularize JavaScript (ES modules or a lightweight bundler) — all JS files are standalone globals; switching to ES modules would enable proper imports and reduce duplication
- [x] Add meta tags and improve SEO — added description, Open Graph, and canonical tags to current-season and 2025 archive pages
- [ ] Add advanced stats (WAR, wOBA, FIP, etc.) on batting/pitching leaderboards and player pages
- [x] Add charts/visualizations for trends, comparisons, and playoff odds (e.g., using Chart.js) — added Chart.js bar charts on batting/pitching leader pages and a career stats line chart on player profiles; the compare page shows a grouped season stats chart when both players are loaded
- [ ] Add end-to-end tests (e.g., Playwright or Cypress) to verify data renders correctly in the browser
- [ ] Run Lighthouse CI in the workflow to track performance, accessibility, and SEO scores over time
- [x] Add print stylesheet (`@media print`) so standings/stats pages print cleanly

---

## 🟢 Low Priority

- [ ] Add playoff picture/bracket visualization (e.g., Wild Card race leaders, projected matchups)
- [x] Add player-vs-player comparison tool (side-by-side career/season stats) — added `compare.html` + `compare.js` with dual player search, bio, season and career stats
- [x] Let users favorite/star teams or players (persisted in `localStorage`) — ⭐ favorite buttons on team/player pages; favorites panel on standings page
- [ ] Add PWA support (installable, offline basic features via a Service Worker)
- [ ] Add a Content Security Policy header if the app is self-hosted, to restrict external script/data sources
- [ ] Integrate MLB news or team/player headlines
- [x] Add social sharing buttons for teams, players, and leaderboards — 🔗 Share button (copies URL to clipboard) on team and player pages
- [ ] Support multiple languages and time zones (localization / `Intl` API)
- [x] Add CSV/JSON export buttons on standings and leader tables so users can download data — ⬇ Export CSV buttons on standings, batting leaders, and pitching leaders
- [ ] Add game alerts or notifications (browser Push API or email) for tracked teams' game results
