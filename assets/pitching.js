const {
    buildChartFallbackTable,
    createFooterUpdater,
    escapeHtml,
    exportSectionToCsv,
    fetchJsonWithRetry,
    getChartTheme,
    initDarkModeToggle,
    setupAccessibleTabs
} = window.MLBUtils;

const currentYear = new Date().getFullYear();
const seasonSelect = document.getElementById('season-select');
const pageTitle = document.getElementById('page-title');
const chartInstances = new Map();
const chartConfigStore = new Map();

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
    if (pageTitle) pageTitle.textContent = `${selectedSeason} MLB Pitching Leaders`;
    document.title = `${selectedSeason} MLB Pitching Leaders`;
}

setPageTitleForSeason();

let updateFooter = createFooterUpdater(selectedSeason);
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

function destroyChartsForContainer(containerId) {
    const current = chartInstances.get(containerId) || [];
    current.forEach((chart) => chart.destroy());
    chartInstances.set(containerId, []);
}

function renderChartsForContainer(containerId, configs) {
    destroyChartsForContainer(containerId);
    if (!window.Chart || !Array.isArray(configs) || configs.length === 0) return;
    const theme = getChartTheme();
    const instances = [];

    configs.forEach((cfg) => {
        const canvas = document.getElementById(cfg.canvasId);
        const fallback = document.getElementById(cfg.fallbackId);
        if (!canvas) return;
        if (fallback && cfg.fallbackHeaders && cfg.fallbackRows) {
            fallback.innerHTML = buildChartFallbackTable(cfg.fallbackCaption, cfg.fallbackHeaders, cfg.fallbackRows);
        }

        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: theme.legendColor } },
                title: {
                    display: Boolean(cfg.title),
                    text: cfg.title,
                    color: theme.legendColor
                }
            }
        };

        const options = cfg.type === 'scatter'
            ? {
                ...commonOptions,
                onClick: (event, elements, chart) => {
                    if (!elements || elements.length === 0) return;
                    const point = chart.data.datasets[0].data[elements[0].index];
                    if (point && point.playerId) {
                        window.location.href = `player.html?playerId=${encodeURIComponent(point.playerId)}`;
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'ERA', color: theme.textColor },
                        ticks: { color: theme.textColor },
                        grid: { color: theme.gridColor }
                    },
                    y: {
                        title: { display: true, text: 'WHIP', color: theme.textColor },
                        ticks: { color: theme.textColor },
                        grid: { color: theme.gridColor }
                    }
                }
            }
            : {
                ...commonOptions,
                indexAxis: 'y',
                onClick: (event, elements) => {
                    if (!elements || elements.length === 0) return;
                    const index = elements[0].index;
                    const playerId = cfg.playerIds && cfg.playerIds[index];
                    if (playerId) window.location.href = `player.html?playerId=${encodeURIComponent(playerId)}`;
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
                },
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false }
                }
            };

        const chart = new Chart(canvas, {
            type: cfg.type,
            data: cfg.data,
            options
        });
        instances.push(chart);
    });

    chartInstances.set(containerId, instances);
}

async function fetchScatterPoints() {
    try {
        const [eraData, whipData] = await Promise.all([
            fetchJsonWithRetry(`https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=era&season=${selectedSeason}&limit=50&statGroup=pitching`, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 }),
            fetchJsonWithRetry(`https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=whip&season=${selectedSeason}&limit=50&statGroup=pitching`, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 })
        ]);

        const eraLeaders = eraData.leagueLeaders && eraData.leagueLeaders[0] ? eraData.leagueLeaders[0].leaders || [] : [];
        const whipLeaders = whipData.leagueLeaders && whipData.leagueLeaders[0] ? whipData.leagueLeaders[0].leaders || [] : [];
        const byPlayer = new Map();

        eraLeaders.forEach((leader) => {
            byPlayer.set(String(leader.person.id), {
                playerId: String(leader.person.id),
                name: leader.person.fullName,
                era: Number.parseFloat(leader.value),
                whip: null
            });
        });

        whipLeaders.forEach((leader) => {
            const id = String(leader.person.id);
            const existing = byPlayer.get(id) || {
                playerId: id,
                name: leader.person.fullName,
                era: null,
                whip: null
            };
            existing.whip = Number.parseFloat(leader.value);
            byPlayer.set(id, existing);
        });

        return Array.from(byPlayer.values()).filter((p) => Number.isFinite(p.era) && Number.isFinite(p.whip));
    } catch (e) {
        return [];
    }
}

async function fetchLeaders(stats, containerId) {
    const target = document.getElementById(containerId);
    target.innerHTML = '<div class="loading-indicator" role="status" aria-live="polite"><span class="loading-spinner" aria-hidden="true"></span><span>Loading pitching leaders…</span></div>';
    let html = '';
    let hasAnyData = false;
    const chartConfigs = [];

    const scatterPoints = await fetchScatterPoints();
    if (scatterPoints.length > 0) {
        const scatterCanvasId = `${containerId}-scatter`;
        const scatterFallbackId = `${containerId}-scatter-fallback`;
        html += `<details class="chart-block" open><summary>📈 ERA vs WHIP scatter</summary><div class="chart-wrap"><canvas id="${scatterCanvasId}" role="img" aria-label="ERA versus WHIP scatter chart"></canvas><div id="${scatterFallbackId}" class="chart-fallback"></div></div></details>`;
        chartConfigs.push({
            type: 'scatter',
            canvasId: scatterCanvasId,
            fallbackId: scatterFallbackId,
            title: `${selectedSeason} ERA vs WHIP (Top Pitchers)`,
            data: {
                datasets: [{
                    label: 'Pitchers',
                    data: scatterPoints.map((p) => ({ x: p.era, y: p.whip, playerId: p.playerId, label: p.name })),
                    pointBackgroundColor: '#ff851b',
                    pointRadius: 4
                }]
            },
            fallbackCaption: `${selectedSeason} ERA vs WHIP`,
            fallbackHeaders: ['Player', 'ERA', 'WHIP'],
            fallbackRows: scatterPoints.map((p) => [p.name, p.era.toFixed(2), p.whip.toFixed(2)])
        });
    }

    for (const stat of stats) {
        html += `<h2>${stat.label} Leaders</h2>`;
        for (const league of ['American League', 'National League']) {
            html += `<h3>${league}</h3>`;
            const leagueId = league === 'American League' ? 103 : 104;
            const sectionId = `${containerId}-${stat.key}-${leagueId}`;
            const canvasId = `${sectionId}-chart`;
            const fallbackId = `${sectionId}-fallback`;
            html += `<details class="chart-block" open><summary>📊 ${escapeHtml(league)} ${escapeHtml(stat.label)} top 10 chart</summary><div class="chart-wrap"><canvas id="${canvasId}" role="img" aria-label="${escapeHtml(league)} ${escapeHtml(stat.label)} leaders chart"></canvas><div id="${fallbackId}" class="chart-fallback"></div></div></details>`;
            html += `<table><thead><tr><th scope="col">Rank</th><th scope="col">Player</th><th scope="col">Team</th><th scope="col">${stat.label}</th></tr></thead><tbody>`;
            try {
                const url = `https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=${stat.key}&season=${selectedSeason}&limit=10&statGroup=pitching&leagueId=${leagueId}`;
                const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
                const leaders = data.leagueLeaders && data.leagueLeaders[0] && data.leagueLeaders[0].leaders ? data.leagueLeaders[0].leaders : [];
                if (leaders.length > 0) hasAnyData = true;
                if (leaders.length === 0) {
                    html += '<tr><td colspan="4">No data available yet</td></tr>';
                }
                for (const leader of leaders) {
                    const playerLink = `player.html?playerId=${leader.person.id}`;
                    html += `<tr><td>${leader.rank}</td><td><a href="${playerLink}">${escapeHtml(leader.person.fullName)}</a></td><td>${escapeHtml(leader.team ? leader.team.name : '')}</td><td>${escapeHtml(String(leader.value))}</td></tr>`;
                }

                if (leaders.length > 0) {
                    chartConfigs.push({
                        type: 'bar',
                        canvasId,
                        fallbackId,
                        title: `${league} ${stat.label} leaders (${selectedSeason})`,
                        data: {
                            labels: leaders.map((leader) => leader.person.fullName),
                            datasets: [{
                                label: stat.label,
                                data: leaders.map((leader) => Number.parseFloat(leader.value) || 0),
                                backgroundColor: '#ff851b'
                            }]
                        },
                        playerIds: leaders.map((leader) => String(leader.person.id)),
                        fallbackCaption: `${league} ${stat.label} leaders (${selectedSeason})`,
                        fallbackHeaders: ['Player', stat.label],
                        fallbackRows: leaders.map((leader) => [leader.person.fullName, leader.value])
                    });
                }
                updateFooter(new Date());
            } catch (e) {
                html += '<tr><td colspan="4">Failed to load data</td></tr>';
            }
            html += '</tbody></table>';
        }
    }

    if (!hasAnyData) {
        html = `<div class="no-data-message"><p>No pitching leader data available yet for the ${selectedSeason} season.</p><p>Check back once games have been played!</p></div>`;
    }

    target.innerHTML = html;
    chartConfigStore.set(containerId, chartConfigs);
    renderChartsForContainer(containerId, chartConfigs);

    if (hasAnyData) {
        const exportBtn = document.createElement('button');
        exportBtn.type = 'button';
        exportBtn.className = 'btn-export';
        exportBtn.textContent = '⬇ Export CSV';
        exportBtn.setAttribute('aria-label', 'Export pitching leaders as CSV');
        exportBtn.addEventListener('click', () => exportSectionToCsv(target, `mlb-pitching-${containerId.replace('pitching-leaders-', '')}-${selectedSeason}.csv`));
        target.prepend(exportBtn);
    }
}

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
        fetchLeaders(basicStats, 'pitching-leaders-basic');
        fetchLeaders(advancedStats, 'pitching-leaders-advanced');
    });
}

window.addEventListener('mlb:themechange', () => {
    chartConfigStore.forEach((configs, containerId) => {
        renderChartsForContainer(containerId, configs);
    });
});

initSeasonSelector();
fetchLeaders(basicStats, 'pitching-leaders-basic');
fetchLeaders(advancedStats, 'pitching-leaders-advanced');
