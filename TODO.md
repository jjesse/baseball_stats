# MLB Web App Improvement Ideas

## User Experience & UI
- Add loading indicators (spinners/progress bars) while data loads
- Show user-friendly error messages for API failures
- Further optimize tables and layout for mobile devices
- Improve accessibility (ARIA labels, color contrast, keyboard navigation)

## Features & Functionality
- Make player names clickable for detailed player profiles
- Add recent results and upcoming games to team pages
- Allow sorting/filtering of leaderboards and standings by any column
- Enable selection of previous seasons for standings and leaders
- Let users favorite/star teams or players
- Add advanced stats (WAR, wOBA, FIP, etc.)
- Add charts/visualizations for trends, comparisons, playoff odds
- Add a global search bar to find teams or players by name
- Add today's live scores/scoreboard as a homepage section or dedicated page
- Add player-vs-player comparison tool (side-by-side career/season stats)
- Add team schedule to team pages (upcoming and recent games)
- Add per-player stats (batting/pitching) on the team roster page, not just name/position/number
- Add playoff picture/bracket visualization (e.g., Wild Card race leaders, projected matchups)
- Add career stats and splits on player profile pages (when player names become clickable)
- Add more years to the archive system — currently only 2025 is archived; automate archiving or add a season dropdown

## Technical/Performance
- Handle API rate limiting gracefully (retry, backoff, cache)
- Modularize JavaScript (ES modules or framework if app grows)
- Add meta tags and improve SEO
- Add PWA support (installable, offline basic features)
- Add CI/CD deployment automation (e.g., GitHub Pages deploy on merge to main) — CI currently only validates, it does not deploy
- Add data freshness timestamp in the footer — currently says "Updated live" but doesn't show when data was last fetched
- Add print stylesheet (`@media print`) so standings/stats pages print cleanly
- Add a Content Security Policy header if the app is self-hosted, to restrict external script/data sources
- Run Lighthouse CI in the workflow to track performance, accessibility, and SEO scores over time

## Testing & Code Quality
- Add unit tests for JavaScript functions (e.g., with Jest or Vitest) — CI currently only does syntax checks, not behavioral tests
- Add end-to-end tests (e.g., Playwright or Cypress) to verify data renders correctly
- Add ESLint to CI for consistent code style enforcement (currently only `node --check` is run)
- Extract shared utilities (dark mode toggle, footer, `escapeHtml`) into a single shared module — the same code is duplicated across all four JS files

## Content & Engagement
- Integrate MLB news or team/player headlines
- Add social sharing buttons for teams, players, leaderboards
- Support multiple languages and time zones (localization)
- Add CSV/JSON export buttons on standings and leader tables so users can download data
- Add game alerts or notifications (browser Push API or email) for tracked teams' game results
