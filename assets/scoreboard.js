// Scoreboard - show today's games with live/final scores and date navigation
const scoreboardDiv = document.getElementById('scoreboard');
const selectedDateSpan = document.getElementById('selected-date');
const currentYear = new Date().getFullYear();
const { createFooterUpdater, escapeHtml, fetchJsonWithRetry, initDarkModeToggle } = window.MLBUtils;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

function formatDateParam(date) {
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    const yyyy = date.getFullYear();
    return `${mm}/${dd}/${yyyy}`;
}

function formatDateDisplay(date) {
    return date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

let viewDate = new Date();
viewDate.setHours(0, 0, 0, 0);

function updatePageTitle() {
    const pageTitle = document.getElementById('page-title');
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const isToday = viewDate.getTime() === today.getTime();
    if (pageTitle) pageTitle.textContent = isToday ? "Today's MLB Scoreboard" : 'MLB Scoreboard';
    document.title = isToday ? "Today's MLB Scoreboard" : `MLB Scoreboard - ${formatDateDisplay(viewDate)}`;
    if (selectedDateSpan) selectedDateSpan.textContent = formatDateDisplay(viewDate);
}

async function fetchScoreboard() {
    updatePageTitle();
    scoreboardDiv.innerHTML = '<p>Loading games...</p>';
    const dateParam = formatDateParam(viewDate);
    try {
        const url = `https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=${dateParam}&hydrate=linescore,decisions`;
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 15000 });
        const dates = data.dates && data.dates.length > 0 ? data.dates : [];
        if (dates.length === 0 || !dates[0].games || dates[0].games.length === 0) {
            scoreboardDiv.innerHTML = '<div class="no-data-message"><p>No games scheduled for this date.</p></div>';
            return;
        }
        const games = dates[0].games;
        let html = '<div class="scoreboard-grid">';
        for (const game of games) {
            const away = game.teams.away;
            const home = game.teams.home;
            const awayTeam = away.team;
            const homeTeam = home.team;
            const awayScore = away.score !== undefined ? away.score : '-';
            const homeScore = home.score !== undefined ? home.score : '-';
            const status = game.status ? game.status.detailedState : '';
            const abstractState = game.status ? game.status.abstractGameState : '';
            const awayLogoUrl = `https://www.mlbstatic.com/team-logos/${awayTeam.id}.svg`;
            const homeLogoUrl = `https://www.mlbstatic.com/team-logos/${homeTeam.id}.svg`;
            const awayLink = `team.html?teamId=${awayTeam.id}`;
            const homeLink = `team.html?teamId=${homeTeam.id}`;
            const awayWin = abstractState === 'Final' && awayScore > homeScore;
            const homeWin = abstractState === 'Final' && homeScore > awayScore;

            let inningInfo = '';
            if (abstractState === 'Live' && game.linescore) {
                const ls = game.linescore;
                const half = ls.isTopInning ? 'Top' : 'Bot';
                inningInfo = `${half} ${ls.currentInningOrdinal || ''}`;
            } else if (abstractState === 'Final') {
                inningInfo = 'Final';
                if (game.linescore && game.linescore.currentInning && game.linescore.currentInning !== 9) {
                    inningInfo += ` (${game.linescore.currentInning})`;
                }
            } else if (game.gameDate) {
                const gameTime = new Date(game.gameDate);
                inningInfo = gameTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });
            } else {
                inningInfo = escapeHtml(status);
            }

            const statusClass = abstractState === 'Live' ? 'status-live' : (abstractState === 'Final' ? 'status-final' : 'status-preview');
            html += `<div class="scoreboard-card">
                <div class="scoreboard-status ${statusClass}">${escapeHtml(inningInfo)}</div>
                <div class="scoreboard-team ${awayWin ? 'winner' : ''}">
                    <a href="${awayLink}"><img src="${awayLogoUrl}" alt="${escapeHtml(awayTeam.name)} logo" class="team-logo"></a>
                    <a href="${awayLink}" class="team-name-link">${escapeHtml(awayTeam.name)}</a>
                    <span class="team-score">${escapeHtml(String(awayScore))}</span>
                </div>
                <div class="scoreboard-team ${homeWin ? 'winner' : ''}">
                    <a href="${homeLink}"><img src="${homeLogoUrl}" alt="${escapeHtml(homeTeam.name)} logo" class="team-logo"></a>
                    <a href="${homeLink}" class="team-name-link">${escapeHtml(homeTeam.name)}</a>
                    <span class="team-score">${escapeHtml(String(homeScore))}</span>
                </div>
            </div>`;
        }
        html += '</div>';
        scoreboardDiv.innerHTML = html;
        updateFooter(new Date());
    } catch (e) {
        scoreboardDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load scoreboard. Please try again later.</p></div>';
    }
}

document.getElementById('prev-day').onclick = function () {
    viewDate.setDate(viewDate.getDate() - 1);
    fetchScoreboard();
};
document.getElementById('next-day').onclick = function () {
    viewDate.setDate(viewDate.getDate() + 1);
    fetchScoreboard();
};

fetchScoreboard();
