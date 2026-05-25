// Fetch MLB standings from the MLB Stats API and render them
// API docs: https://statsapi.mlb.com/api/

const standingsDiv = document.getElementById('standings');
const currentYear = new Date().getFullYear();
const seasonSelect = document.getElementById('season-select');
const pageTitle = document.getElementById('page-title');
const {
    buildChartFallbackTable,
    createFooterUpdater,
    escapeHtml,
    exportSectionToCsv,
    fetchJsonWithRetry,
    getChartTheme,
    getFavorites,
    initDarkModeToggle,
    makeSortableHeadersAccessible
} = window.MLBUtils;

function getInitialSeason() {
    const params = new URLSearchParams(window.location.search);
    const raw = params.get('season');
    if (raw && /^\d{4}$/.test(raw)) {
        const season = Number(raw);
        if (season >= 1901 && season <= currentYear) return season;
    }
    return currentYear;
}

let selectedSeason = getInitialSeason();

function setPageTitleForSeason() {
    if (pageTitle) pageTitle.textContent = `${selectedSeason} MLB Standings`;
    document.title = `${selectedSeason} MLB Standings`;
}

setPageTitleForSeason();

let updateFooter = createFooterUpdater(selectedSeason);
initDarkModeToggle();

function renderFavoritesSection() {
    const section = document.getElementById('favorites-section');
    if (!section) return;
    const { teams, players } = getFavorites();
    if (teams.length === 0 && players.length === 0) {
        section.innerHTML = '';
        return;
    }
    let html = '<div class="favorites-panel"><h2>⭐ Favorites</h2><ul class="favorites-list">';
    teams.forEach((t) => {
        html += `<li><a href="team.html?teamId=${encodeURIComponent(t.id)}">🏟️ ${escapeHtml(t.name)}</a></li>`;
    });
    players.forEach((p) => {
        html += `<li><a href="player.html?playerId=${encodeURIComponent(p.id)}">👤 ${escapeHtml(p.name)}</a></li>`;
    });
    html += '</ul></div>';
    section.innerHTML = html;
}

renderFavoritesSection();
window.addEventListener('storage', (e) => {
    if (e.key === 'mlbFavorites') renderFavoritesSection();
});

let currentSort = { key: null, asc: true };
let divisionWinsCharts = [];
let latestDivisionChartData = [];

function destroyDivisionCharts() {
    divisionWinsCharts.forEach((chart) => chart.destroy());
    divisionWinsCharts = [];
}

function renderDivisionWinsCharts(chartDataList) {
    destroyDivisionCharts();
    if (!window.Chart || !Array.isArray(chartDataList) || chartDataList.length === 0) return;
    const theme = getChartTheme();
    chartDataList.forEach((chartData) => {
        const canvas = document.getElementById(chartData.canvasId);
        const fallback = document.getElementById(chartData.fallbackId);
        if (!canvas) return;
        if (fallback) {
            const rows = chartData.labels.map((label, idx) => [label, chartData.values[idx]]);
            fallback.innerHTML = buildChartFallbackTable(`${chartData.title} data`, ['Team', 'Wins'], rows);
        }
        const chart = new window.Chart(canvas, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Wins',
                    data: chartData.values,
                    backgroundColor: chartData.colors
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: chartData.title,
                        color: theme.legendColor
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
        divisionWinsCharts.push(chart);
    });
}

async function fetchStandings() {
    standingsDiv.innerHTML = '<div class="loading-indicator" role="status" aria-live="polite"><span class="loading-spinner" aria-hidden="true"></span><span>Loading standings…</span></div>';
    const url = `https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=${selectedSeason}&standingsTypes=regularSeason`;
    try {
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
        renderStandings(data);
        updateFooter(new Date());
    } catch (e) {
        standingsDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load standings.</p><p>The season may not have started yet, or the data service is temporarily unavailable. Please try again later.</p></div>';
    }
}

function renderStandings(data) {
    if (!data.records || !Array.isArray(data.records) || data.records.length === 0) {
        standingsDiv.innerHTML = `<div class="no-data-message"><p>No standings data available yet for the ${selectedSeason} season.</p><p>Check back once games have been played!</p></div>`;
        return;
    }

    const leagues = {};
    data.records.forEach((record) => {
        let leagueName = record.league && record.league.name ? record.league.name : '';
        if (!leagueName && record.league && record.league.id === 103) leagueName = 'American League';
        if (!leagueName && record.league && record.league.id === 104) leagueName = 'National League';
        if (!leagues[leagueName]) leagues[leagueName] = [];
        leagues[leagueName].push(record);
    });

    latestDivisionChartData = [];
    let html = '';
    for (const [league, divisions] of Object.entries(leagues)) {
        if (league && league !== 'undefined') {
            html += `<section class="league-section"><h2 class="league-header">${escapeHtml(league)}</h2>`;
        }

        divisions.forEach((division) => {
            let divisionName = division.division && division.division.name ? division.division.name : '';
            if (!divisionName && division.division && division.division.id) {
                const divisionId = division.division.id;
                if (divisionId === 201) divisionName = 'American League East';
                if (divisionId === 202) divisionName = 'American League Central';
                if (divisionId === 200) divisionName = 'American League West';
                if (divisionId === 204) divisionName = 'National League East';
                if (divisionId === 205) divisionName = 'National League Central';
                if (divisionId === 203) divisionName = 'National League West';
            }

            const divisionChartIdSafe = `${(divisionName || 'division').toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${selectedSeason}`;
            const canvasId = `wins-chart-${divisionChartIdSafe}`;
            const fallbackId = `wins-chart-fallback-${divisionChartIdSafe}`;
            html += '<div class="division-section">';
            if (divisionName && divisionName !== 'undefined') {
                html += `<h3 class="division-header">${escapeHtml(divisionName)}</h3>`;
            }
            html += `
                <details class="chart-block" open>
                    <summary>📈 Division wins chart</summary>
                    <div class="chart-wrap">
                        <canvas id="${canvasId}" aria-label="${escapeHtml(divisionName || 'Division')} wins bar chart" role="img"></canvas>
                        <div id="${fallbackId}" class="chart-fallback"></div>
                    </div>
                </details>`;

            html += `<table><thead><tr>
                <th scope="col">Team</th>
                <th class="sortable" data-sort="wins" scope="col">W</th>
                <th class="sortable" data-sort="losses" scope="col">L</th>
                <th class="sortable" data-sort="winningPercentage" scope="col">Pct</th>
                <th scope="col">GB</th>
                <th scope="col">Streak</th>
                <th scope="col">Lg/Div Rank</th>
                <th scope="col">Magic #</th>
                <th scope="col">Status</th></tr></thead><tbody>`;

            const teamRecords = [...division.teamRecords];
            if (currentSort.key) {
                teamRecords.sort((a, b) => {
                    let valA = a[currentSort.key];
                    let valB = b[currentSort.key];
                    if (currentSort.key === 'winningPercentage') {
                        valA = parseFloat(valA);
                        valB = parseFloat(valB);
                    } else {
                        valA = Number(valA);
                        valB = Number(valB);
                    }
                    return currentSort.asc ? valA - valB : valB - valA;
                });
            }

            const chartLabels = [];
            const chartValues = [];
            const chartColors = [];
            teamRecords.forEach((team) => {
                let status = '';
                if (team.clinched) {
                    status = 'Clinched Playoff Spot';
                } else if (team.divisionChamp) {
                    status = 'Clinched Division';
                } else if (team.wildCardLeader) {
                    status = 'Wild Card Leader';
                } else if (team.hasWildcard) {
                    if (team.wildCardEliminationNumber !== 'E' && team.wildCardEliminationNumber !== 0 && team.wildCardEliminationNumber !== '0') {
                        status = 'In Wild Card Race';
                    } else {
                        status = 'Eliminated';
                    }
                }
                const logoUrl = `https://www.mlbstatic.com/team-logos/${team.team.id}.svg`;
                const streak = team.streak && team.streak.streakCode ? team.streak.streakCode : '';
                const rank = `Lg: ${team.leagueRank || ''} / Div: ${team.divisionRank || ''}`;
                const magic = team.magicNumber !== undefined && team.magicNumber !== null ? team.magicNumber : '';
                const teamLink = `team.html?teamId=${team.team.id}`;
                const winningPct = Number.parseFloat(team.winningPercentage);
                const pctPercent = Number.isFinite(winningPct) ? Math.max(0, Math.min(100, winningPct * 100)) : 0;
                html += `<tr><td><a href="${teamLink}"><img src="${logoUrl}" alt="${escapeHtml(team.team.name)} logo" class="team-logo"> ${escapeHtml(team.team.name)}</a></td><td>${team.wins}</td><td>${team.losses}</td><td><div class="win-pct-cell"><span>${escapeHtml(String(team.winningPercentage || ''))}</span><span class="win-pct-bar-track"><span class="win-pct-bar-fill" style="width:${pctPercent.toFixed(1)}%" aria-hidden="true"></span></span></div></td><td>${escapeHtml(String(team.gamesBack || ''))}</td><td>${escapeHtml(streak)}</td><td>${escapeHtml(rank)}</td><td>${escapeHtml(String(magic))}</td><td>${escapeHtml(status)}</td></tr>`;
                chartLabels.push(team.team.name);
                chartValues.push(Number(team.wins) || 0);
                chartColors.push('#0074d9');
            });
            latestDivisionChartData.push({
                canvasId,
                fallbackId,
                title: `${divisionName || 'Division'} wins`,
                labels: chartLabels,
                values: chartValues,
                colors: chartColors
            });
            html += '</tbody></table></div>';
        });
        html += '</section>';
    }

    standingsDiv.innerHTML = html;
    renderDivisionWinsCharts(latestDivisionChartData);

    const exportBtn = document.createElement('button');
    exportBtn.type = 'button';
    exportBtn.className = 'btn-export';
    exportBtn.textContent = '⬇ Export CSV';
    exportBtn.setAttribute('aria-label', `Export ${selectedSeason} standings as CSV`);
    exportBtn.addEventListener('click', () => exportSectionToCsv(standingsDiv, `mlb-standings-${selectedSeason}.csv`));
    standingsDiv.insertBefore(exportBtn, standingsDiv.firstChild);

    makeSortableHeadersAccessible(
        '.sortable',
        (th) => {
            const key = th.getAttribute('data-sort');
            if (currentSort.key === key) {
                currentSort.asc = !currentSort.asc;
            } else {
                currentSort.key = key;
                currentSort.asc = false;
            }

            fetchStandings();
        },
        (th) => {
            const key = th.getAttribute('data-sort');
            if (currentSort.key !== key) return 'none';
            return currentSort.asc ? 'ascending' : 'descending';
        }
    );
}

window.addEventListener('mlb:themechange', () => {
    renderDivisionWinsCharts(latestDivisionChartData);
});

function updateSeasonQueryParam() {
    const url = new URL(window.location.href);
    url.searchParams.set('season', String(selectedSeason));
    window.history.replaceState({}, '', url);
}

function initSeasonSelector() {
    if (!seasonSelect) return;
    let optionsHtml = '';
    for (let season = currentYear; season >= 1901; season -= 1) {
        optionsHtml += `<option value="${season}"${season === selectedSeason ? ' selected' : ''}>${season}</option>`;
    }
    seasonSelect.innerHTML = optionsHtml;

    seasonSelect.addEventListener('change', () => {
        selectedSeason = Number(seasonSelect.value);
        setPageTitleForSeason();
        updateFooter = createFooterUpdater(selectedSeason);
        updateSeasonQueryParam();
        fetchStandings();
    });
}

initSeasonSelector();
fetchStandings();
