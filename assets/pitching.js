const { createFooterUpdater, fetchJsonWithRetry, initDarkModeToggle, setupAccessibleTabs } = window.MLBUtils;
const currentYear = new Date().getFullYear();
const pageTitle = document.getElementById('page-title');

if (pageTitle) pageTitle.textContent = `${currentYear} MLB Pitching Leaders`;
document.title = `${currentYear} MLB Pitching Leaders`;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

setupAccessibleTabs({
    tabSelector: '.tab-btn',
    panelPrefix: 'pitching-leaders-',
    idPrefix: 'pitching-tab'
});

const basicStats = [
    { key: 'wins', label: 'W' },
    { key: 'era', label: 'ERA' },
    { key: 'strikeouts', label: 'K' },
    { key: 'saves', label: 'SV' },
    { key: 'whip', label: 'WHIP' },
    { key: 'inningsPitched', label: 'IP' },
    { key: 'opponentBattingAvg', label: 'OBA' }
];
const advancedStats = [
    { key: 'whip', label: 'WHIP' },
    { key: 'kPer9', label: 'K/9' },
    { key: 'bbPer9', label: 'BB/9' },
    { key: 'hrPer9', label: 'HR/9' },
    { key: 'opponentBattingAvg', label: 'OBA' }
];

async function fetchLeaders(stats, containerId) {
    let html = '';
    let hasAnyData = false;
    for (const stat of stats) {
        html += `<h2>${stat.label} Leaders</h2>`;
        for (const league of ['American League', 'National League']) {
            html += `<h3>${league}</h3>`;
            html += `<table><thead><tr><th scope="col">Rank</th><th scope="col">Player</th><th scope="col">Team</th><th scope="col">${stat.label}</th></tr></thead><tbody>`;
            try {
                const leagueId = league === 'American League' ? 103 : 104;
                const url = `https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=${stat.key}&season=${currentYear}&limit=10&statGroup=pitching&leagueId=${leagueId}`;
                const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
                const leaders = data.leagueLeaders && data.leagueLeaders[0] && data.leagueLeaders[0].leaders ? data.leagueLeaders[0].leaders : [];
                if (leaders.length > 0) hasAnyData = true;
                if (leaders.length === 0) {
                    html += '<tr><td colspan="4">No data available yet</td></tr>';
                }
                for (const leader of leaders) {
                    const playerLink = `player.html?playerId=${leader.person.id}`;
                    html += `<tr><td>${leader.rank}</td><td><a href="${playerLink}">${leader.person.fullName}</a></td><td>${leader.team ? leader.team.name : ''}</td><td>${leader.value}</td></tr>`;
                }
                updateFooter(new Date());
            } catch (e) {
                html += '<tr><td colspan="4">Failed to load data</td></tr>';
            }
            html += '</tbody></table>';
        }
    }
    if (!hasAnyData) {
        html = `<div class="no-data-message"><p>No pitching leader data available yet for the ${currentYear} season.</p><p>Check back once games have been played!</p></div>`;
    }
    document.getElementById(containerId).innerHTML = html;
}

fetchLeaders(basicStats, 'pitching-leaders-basic');
fetchLeaders(advancedStats, 'pitching-leaders-advanced');
