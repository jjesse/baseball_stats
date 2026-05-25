// Player profile page - shows bio, career stats, season stats, and splits
const playerNameHeader = document.getElementById('player-name');
const playerInfoDiv = document.getElementById('player-info');
const currentYear = new Date().getFullYear();
const {
    buildChartFallbackTable,
    createFooterUpdater,
    escapeHtml,
    fetchJsonWithRetry,
    getChartTheme,
    initDarkModeToggle,
    isFavorite,
    setupAccessibleTabs,
    toggleFavorite
} = window.MLBUtils;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

let careerChart = null;
let splitsChart = null;
let latestCareerStats = null;
let latestSplitsStats = null;
let latestStatGroup = 'hitting';

function destroyCareerChart() {
    if (careerChart) {
        careerChart.destroy();
        careerChart = null;
    }
}

function destroySplitsChart() {
    if (splitsChart) {
        splitsChart.destroy();
        splitsChart = null;
    }
}

function renderCareerTrendChart(stats, statGroup) {
    destroyCareerChart();
    latestCareerStats = stats;
    latestStatGroup = statGroup;
    if (!window.Chart || !Array.isArray(stats) || stats.length === 0) return;

    const canvas = document.getElementById('player-career-trend-chart');
    const fallback = document.getElementById('player-career-chart-fallback');
    if (!canvas) return;

    const seasons = stats.map((row) => String(row.season || ''));
    const metricConfig = statGroup === 'hitting'
        ? [
            { key: 'avg', label: 'AVG', color: '#0074d9' },
            { key: 'homeRuns', label: 'HR', color: '#2ecc40' },
            { key: 'ops', label: 'OPS', color: '#b10dc9' }
        ]
        : [
            { key: 'era', label: 'ERA', color: '#ff4136' },
            { key: 'whip', label: 'WHIP', color: '#ff851b' },
            { key: 'strikeOuts', label: 'K', color: '#0074d9' }
        ];

    const datasets = metricConfig.map((metric) => ({
        label: metric.label,
        data: stats.map((row) => {
            const raw = row.stat && row.stat[metric.key] !== undefined ? row.stat[metric.key] : null;
            const parsed = Number.parseFloat(raw);
            return Number.isFinite(parsed) ? parsed : null;
        }),
        borderColor: metric.color,
        backgroundColor: metric.color,
        tension: 0.2,
        spanGaps: true
    }));

    if (fallback) {
        const fallbackRows = stats.map((row) => {
            const season = row.season || '';
            return [season, ...metricConfig.map((metric) => row.stat && row.stat[metric.key] !== undefined ? row.stat[metric.key] : '')];
        });
        fallback.innerHTML = buildChartFallbackTable(
            `${currentYear} career trend data`,
            ['Season', ...metricConfig.map((metric) => metric.label)],
            fallbackRows
        );
    }

    const theme = getChartTheme();
    careerChart = new window.Chart(canvas, {
        type: 'line',
        data: { labels: seasons, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Career trend by season',
                    color: theme.legendColor
                },
                legend: {
                    labels: { color: theme.legendColor }
                }
            },
            scales: {
                x: {
                    ticks: { color: theme.textColor },
                    grid: { color: theme.gridColor }
                },
                y: {
                    ticks: { color: theme.textColor },
                    grid: { color: theme.gridColor }
                }
            }
        }
    });
}

function renderSplitsChart(splits, statGroup) {
    destroySplitsChart();
    latestSplitsStats = splits;
    latestStatGroup = statGroup;
    if (!window.Chart || !Array.isArray(splits) || splits.length === 0) return;

    const canvas = document.getElementById('player-splits-chart');
    const fallback = document.getElementById('player-splits-chart-fallback');
    if (!canvas) return;

    const labels = splits.map((row) => row.split ? row.split.description : 'Split');
    const metricConfig = statGroup === 'hitting'
        ? [
            { key: 'avg', label: 'AVG', color: '#0074d9' },
            { key: 'obp', label: 'OBP', color: '#2ecc40' },
            { key: 'slg', label: 'SLG', color: '#b10dc9' }
        ]
        : [
            { key: 'era', label: 'ERA', color: '#ff4136' },
            { key: 'whip', label: 'WHIP', color: '#ff851b' },
            { key: 'strikeOuts', label: 'K', color: '#0074d9' }
        ];

    const datasets = metricConfig.map((metric) => ({
        label: metric.label,
        data: splits.map((row) => {
            const raw = row.stat && row.stat[metric.key] !== undefined ? row.stat[metric.key] : null;
            const parsed = Number.parseFloat(raw);
            return Number.isFinite(parsed) ? parsed : 0;
        }),
        backgroundColor: metric.color
    }));

    if (fallback) {
        const fallbackRows = splits.map((row) => {
            const splitName = row.split ? row.split.description : 'Split';
            return [splitName, ...metricConfig.map((metric) => row.stat && row.stat[metric.key] !== undefined ? row.stat[metric.key] : '')];
        });
        fallback.innerHTML = buildChartFallbackTable(
            `${currentYear} splits chart data`,
            ['Split', ...metricConfig.map((metric) => metric.label)],
            fallbackRows
        );
    }

    const theme = getChartTheme();
    splitsChart = new window.Chart(canvas, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${currentYear} split comparison`,
                    color: theme.legendColor
                },
                legend: {
                    labels: { color: theme.legendColor }
                }
            },
            scales: {
                x: {
                    ticks: { color: theme.textColor },
                    grid: { color: theme.gridColor }
                },
                y: {
                    ticks: { color: theme.textColor },
                    grid: { color: theme.gridColor }
                }
            }
        }
    });
}

const shareBtn = document.getElementById('shareBtn');
if (shareBtn) {
    shareBtn.addEventListener('click', () => {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(window.location.href).then(() => {
                shareBtn.textContent = '✓ Copied!';
                setTimeout(() => { shareBtn.textContent = '🔗 Share'; }, 2000);
            }).catch(() => {});
        }
    });
}

function getPlayerIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const rawId = params.get('playerId');
    if (rawId && /^\d+$/.test(rawId)) return rawId;
    return null;
}

setupAccessibleTabs({
    tabSelector: '.tab-btn',
    panelPrefix: 'player-',
    idPrefix: 'player-tab'
});

async function fetchPlayerInfo(playerId) {
    try {
        const url = `https://statsapi.mlb.com/api/v1/people/${playerId}?hydrate=currentTeam`;
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
        const person = data.people && data.people[0];
        if (!person) {
            playerInfoDiv.innerHTML = '<div class="no-data-message"><p>Player not found.</p></div>';
            return null;
        }
        playerNameHeader.textContent = person.fullName;
        document.title = `${person.fullName} - MLB Player Profile`;
        const teamName = person.currentTeam ? escapeHtml(person.currentTeam.name) : 'N/A';
        const teamId = person.currentTeam ? person.currentTeam.id : null;
        const teamLink = teamId ? `<a href="team.html?teamId=${teamId}">${teamName}</a>` : teamName;
        const pos = person.primaryPosition ? escapeHtml(person.primaryPosition.abbreviation) : 'N/A';
        const bats = escapeHtml(person.batSide ? person.batSide.description : 'N/A');
        const throws = escapeHtml(person.pitchHand ? person.pitchHand.description : 'N/A');
        const dob = escapeHtml(person.birthDate || 'N/A');
        const birthCity = escapeHtml(person.birthCity || '');
        const birthCountry = escapeHtml(person.birthCountry || '');
        const birthplace = [birthCity, birthCountry].filter(Boolean).join(', ') || 'N/A';
        const height = escapeHtml(person.height || 'N/A');
        const weight = person.weight ? `${person.weight} lbs` : 'N/A';
        playerInfoDiv.innerHTML = `
            <div class="player-bio">
                <p><strong>Team:</strong> ${teamLink}</p>
                <p><strong>Position:</strong> ${pos}</p>
                <p><strong>Bats/Throws:</strong> ${bats}/${throws}</p>
                <p><strong>Born:</strong> ${dob} in ${birthplace}</p>
                <p><strong>Height/Weight:</strong> ${height} / ${weight}</p>
            </div>`;

        const favBtn = document.createElement('button');
        favBtn.type = 'button';
        favBtn.className = 'btn-favorite';
        const favored = isFavorite('players', playerId);
        favBtn.textContent = favored ? '⭐ Favorited' : '☆ Add to Favorites';
        favBtn.setAttribute('aria-pressed', favored ? 'true' : 'false');
        favBtn.addEventListener('click', () => {
            const nowFav = toggleFavorite('players', playerId, person.fullName);
            favBtn.textContent = nowFav ? '⭐ Favorited' : '☆ Add to Favorites';
            favBtn.setAttribute('aria-pressed', nowFav ? 'true' : 'false');
        });
        playerInfoDiv.appendChild(favBtn);

        const compareLink = document.createElement('a');
        compareLink.href = `compare.html?p1=${encodeURIComponent(playerId)}`;
        compareLink.textContent = '⚔️ Compare with another player';
        compareLink.style.marginLeft = '10px';
        compareLink.style.fontSize = '0.9em';
        playerInfoDiv.appendChild(compareLink);

        updateFooter(new Date());
        return person;
    } catch (e) {
        playerInfoDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load player info. Please try again later.</p></div>';
        return null;
    }
}

function buildStatsTable(stats, statGroup) {
    if (!stats || stats.length === 0) return '<div class="no-data-message"><p>No stats available.</p></div>';
    let keys;
    if (statGroup === 'hitting') {
        keys = ['season', 'gamesPlayed', 'atBats', 'hits', 'doubles', 'triples', 'homeRuns', 'rbi', 'runs', 'stolenBases', 'avg', 'obp', 'slg', 'ops'];
    } else {
        keys = ['season', 'gamesPlayed', 'wins', 'losses', 'era', 'gamesStarted', 'saves', 'inningsPitched', 'strikeOuts', 'baseOnBalls', 'whip', 'avg'];
    }
    const headers = {
        season: 'Season', gamesPlayed: 'G', atBats: 'AB', hits: 'H', doubles: '2B', triples: '3B',
        homeRuns: 'HR', rbi: 'RBI', runs: 'R', stolenBases: 'SB', avg: 'AVG', obp: 'OBP',
        slg: 'SLG', ops: 'OPS', wins: 'W', losses: 'L', era: 'ERA', gamesStarted: 'GS',
        saves: 'SV', inningsPitched: 'IP', strikeOuts: 'K', baseOnBalls: 'BB', whip: 'WHIP'
    };
    let html = '<table><thead><tr>';
    keys.forEach((k) => { html += `<th scope="col">${headers[k] || k}</th>`; });
    html += '</tr></thead><tbody>';
    stats.forEach((row) => {
        const s = row.stat;
        const seasonLabel = row.season || (row.sport ? row.sport.name : '');
        html += '<tr>';
        keys.forEach((k) => {
            if (k === 'season') {
                html += `<td>${escapeHtml(String(seasonLabel || ''))}</td>`;
            } else {
                html += `<td>${escapeHtml(String(s[k] !== undefined && s[k] !== null ? s[k] : ''))}</td>`;
            }
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
}

async function fetchCareerStats(playerId, statGroup) {
    const careerDiv = document.getElementById('player-career');
    try {
        const url = `https://statsapi.mlb.com/api/v1/people/${playerId}/stats?stats=yearByYear&group=${statGroup}&sportId=1`;
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
        const stats = data.stats && data.stats[0] && data.stats[0].splits ? data.stats[0].splits : [];
        if (stats.length === 0) {
            destroyCareerChart();
            latestCareerStats = null;
            careerDiv.innerHTML = '<div class="no-data-message"><p>No career stats available.</p></div>';
        } else {
            careerDiv.innerHTML = `<h2>Career Stats (Year by Year)</h2><details class="chart-block" open><summary>📈 Career trend chart</summary><div class="chart-wrap"><canvas id="player-career-trend-chart" role="img" aria-label="Career trend chart"></canvas><div id="player-career-chart-fallback" class="chart-fallback"></div></div></details>${buildStatsTable(stats, statGroup)}`;
            renderCareerTrendChart(stats, statGroup);
        }
        updateFooter(new Date());
    } catch (e) {
        careerDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load career stats. Please try again later.</p></div>';
    }
}

async function fetchSeasonStats(playerId, statGroup) {
    const seasonDiv = document.getElementById('player-season');
    try {
        const url = `https://statsapi.mlb.com/api/v1/people/${playerId}/stats?stats=season&season=${currentYear}&group=${statGroup}&sportId=1`;
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
        const stats = data.stats && data.stats[0] && data.stats[0].splits ? data.stats[0].splits : [];
        if (stats.length === 0) {
            seasonDiv.innerHTML = `<div class="no-data-message"><p>No ${currentYear} season stats available yet.</p></div>`;
        } else {
            seasonDiv.innerHTML = `<h2>${currentYear} Season Stats</h2>${buildStatsTable(stats, statGroup)}`;
        }
        updateFooter(new Date());
    } catch (e) {
        seasonDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load season stats. Please try again later.</p></div>';
    }
}

async function fetchSplits(playerId, statGroup) {
    const splitsDiv = document.getElementById('player-splits');
    try {
        const url = `https://statsapi.mlb.com/api/v1/people/${playerId}/stats?stats=statSplits&season=${currentYear}&group=${statGroup}&sportId=1&sitCodes=vl,vr`;
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
        const splits = data.stats && data.stats[0] && data.stats[0].splits ? data.stats[0].splits : [];
        if (splits.length === 0) {
            destroySplitsChart();
            latestSplitsStats = null;
            splitsDiv.innerHTML = `<div class="no-data-message"><p>No ${currentYear} splits data available yet.</p></div>`;
        } else {
            let html = `<h2>${currentYear} Splits</h2><details class="chart-block" open><summary>📊 Splits comparison chart</summary><div class="chart-wrap"><canvas id="player-splits-chart" role="img" aria-label="Player splits chart"></canvas><div id="player-splits-chart-fallback" class="chart-fallback"></div></div></details><table><thead><tr><th scope="col">Split</th>`;
            const keys = statGroup === 'hitting'
                ? ['gamesPlayed', 'atBats', 'hits', 'homeRuns', 'rbi', 'avg', 'obp', 'slg', 'ops']
                : ['gamesPlayed', 'wins', 'losses', 'era', 'inningsPitched', 'strikeOuts', 'whip'];
            const headers = {
                gamesPlayed: 'G', atBats: 'AB', hits: 'H', homeRuns: 'HR', rbi: 'RBI',
                avg: 'AVG', obp: 'OBP', slg: 'SLG', ops: 'OPS', wins: 'W', losses: 'L',
                era: 'ERA', inningsPitched: 'IP', strikeOuts: 'K', whip: 'WHIP'
            };
            keys.forEach((k) => { html += `<th scope="col">${headers[k] || k}</th>`; });
            html += '</tr></thead><tbody>';
            splits.forEach((row) => {
                html += `<tr><td>${escapeHtml(row.split ? row.split.description : '')}</td>`;
                keys.forEach((k) => {
                    html += `<td>${escapeHtml(String(row.stat[k] !== undefined && row.stat[k] !== null ? row.stat[k] : ''))}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table>';
            splitsDiv.innerHTML = html;
            renderSplitsChart(splits, statGroup);
        }
        updateFooter(new Date());
    } catch (e) {
        splitsDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load splits. Please try again later.</p></div>';
    }
}

window.addEventListener('mlb:themechange', () => {
    if (latestCareerStats && latestCareerStats.length > 0) renderCareerTrendChart(latestCareerStats, latestStatGroup);
    if (latestSplitsStats && latestSplitsStats.length > 0) renderSplitsChart(latestSplitsStats, latestStatGroup);
});

async function init() {
    const playerId = getPlayerIdFromUrl();
    if (!playerId) {
        playerInfoDiv.innerHTML = '<div class="no-data-message"><p>No player selected.</p></div>';
        document.getElementById('player-stats').style.display = 'none';
        return;
    }

    const person = await fetchPlayerInfo(playerId);
    let statGroup = 'hitting';
    if (person && person.primaryPosition) {
        const pos = person.primaryPosition.abbreviation;
        if (pos === 'P' || pos === 'SP' || pos === 'RP' || pos === 'CL') {
            statGroup = 'pitching';
        }
    }
    latestStatGroup = statGroup;
    fetchCareerStats(playerId, statGroup);
    fetchSeasonStats(playerId, statGroup);
    fetchSplits(playerId, statGroup);
}

init();
