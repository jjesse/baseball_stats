/* global Chart */
const { createFooterUpdater, exportSectionToCsv, fetchJsonWithRetry, initDarkModeToggle, setupAccessibleTabs } = window.MLBUtils;
const currentYear = new Date().getFullYear();
const seasonSelect = document.getElementById('season-select');
const pageTitle = document.getElementById('page-title');

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
    if (pageTitle) pageTitle.textContent = `${selectedSeason} MLB Batting Leaders`;
    document.title = `${selectedSeason} MLB Batting Leaders`;
}

setPageTitleForSeason();

let updateFooter = createFooterUpdater(selectedSeason);
initDarkModeToggle();

setupAccessibleTabs({
    tabSelector: '.tab-btn',
    panelPrefix: 'batting-leaders-',
    idPrefix: 'batting-tab'
});

const basicStats = [
    { key: 'avg', label: 'AVG' },
    { key: 'homeRuns', label: 'HR' },
    { key: 'rbi', label: 'RBI' },
    { key: 'hits', label: 'H' },
    { key: 'runs', label: 'R' },
    { key: 'stolenBases', label: 'SB' }
];
const advancedStats = [
    { key: 'obp', label: 'OBP' },
    { key: 'slg', label: 'SLG' },
    { key: 'ops', label: 'OPS' }
];

// Keys for which we show charts (basic tab only — active on page load)
const BATTING_CHART_KEYS = ['avg', 'homeRuns', 'rbi'];
let activeBattingCharts = [];

function getChartTheme() {
    const s = getComputedStyle(document.body);
    return {
        text: s.getPropertyValue('--clr-text').trim() || '#1a2035',
        muted: s.getPropertyValue('--clr-text-muted').trim() || '#64748b',
        grid: s.getPropertyValue('--clr-border').trim() || '#d1dce8'
    };
}

function buildLeaderBarChart(canvas, label, leaders) {
    if (typeof Chart === 'undefined') return null;
    const theme = getChartTheme();
    const top = leaders.slice(0, 10);
    return new Chart(canvas, {
        type: 'bar',
        data: {
            labels: top.map(l => `${l.name} (${l.league})`),
            datasets: [{
                label,
                data: top.map(l => l.value),
                backgroundColor: top.map(l => l.league === 'AL' ? 'rgba(4,30,66,0.82)' : 'rgba(213,0,50,0.82)'),
                borderRadius: 3,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (ctx) => `${label}: ${ctx.raw}` } }
            },
            scales: {
                x: {
                    ticks: { color: theme.text, font: { size: 11 } },
                    grid: { color: theme.grid }
                },
                y: {
                    ticks: { color: theme.text, font: { size: 11 } },
                    grid: { color: theme.grid }
                }
            }
        }
    });
}

function renderLeaderCharts(target, chartDataMap) {
    if (typeof Chart === 'undefined') return;
    activeBattingCharts.forEach(c => c.destroy());
    activeBattingCharts = [];
    const entries = Object.values(chartDataMap);
    if (entries.length === 0) return;

    const section = document.createElement('div');
    section.className = 'charts-section';

    const legend = document.createElement('div');
    legend.className = 'chart-legend';
    legend.innerHTML = '<span class="chart-legend-item"><span class="chart-legend-dot" style="background:rgba(4,30,66,0.82)"></span>American League</span>'
        + '<span class="chart-legend-item"><span class="chart-legend-dot" style="background:rgba(213,0,50,0.82)"></span>National League</span>';
    section.appendChild(legend);

    const grid = document.createElement('div');
    grid.className = 'charts-grid';
    entries.forEach(({ label, leaders }) => {
        const card = document.createElement('div');
        card.className = 'chart-card';
        const title = document.createElement('p');
        title.className = 'chart-card-title';
        title.textContent = `${label} Leaders`;
        const wrap = document.createElement('div');
        wrap.className = 'chart-canvas-wrap';
        const canvas = document.createElement('canvas');
        canvas.setAttribute('aria-label', `${label} leaders bar chart`);
        canvas.setAttribute('role', 'img');
        wrap.appendChild(canvas);
        card.append(title, wrap);
        grid.appendChild(card);
        const chart = buildLeaderBarChart(canvas, label, leaders);
        if (chart) activeBattingCharts.push(chart);
    });
    section.appendChild(grid);

    const exportBtn = target.querySelector('.btn-export');
    if (exportBtn) {
        exportBtn.insertAdjacentElement('afterend', section);
    } else {
        target.insertBefore(section, target.firstChild);
    }
}

async function fetchLeaders(stats, containerId) {
    const target = document.getElementById(containerId);
    target.innerHTML = '<div class="loading-indicator" role="status" aria-live="polite"><span class="loading-spinner" aria-hidden="true"></span><span>Loading batting leaders…</span></div>';
    let html = '';
    let hasAnyData = false;
    const wantCharts = containerId === 'batting-leaders-basic';
    const chartDataMap = {};
    for (const stat of stats) {
        const collectChart = wantCharts && BATTING_CHART_KEYS.includes(stat.key);
        const statLeaders = [];
        html += `<h2>${stat.label} Leaders</h2>`;
        for (const league of ['American League', 'National League']) {
            html += `<h3>${league}</h3>`;
            html += `<table><thead><tr><th scope="col">Rank</th><th scope="col">Player</th><th scope="col">Team</th><th scope="col">${stat.label}</th></tr></thead><tbody>`;
            try {
                const leagueId = league === 'American League' ? 103 : 104;
                const url = `https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=${stat.key}&season=${selectedSeason}&limit=10&statGroup=hitting&leagueId=${leagueId}`;
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
                if (collectChart) {
                    const leagueCode = league === 'American League' ? 'AL' : 'NL';
                    leaders.slice(0, 5).forEach(l => statLeaders.push({
                        name: l.person.fullName,
                        value: parseFloat(l.value),
                        league: leagueCode
                    }));
                }
                updateFooter(new Date());
            } catch (e) {
                html += '<tr><td colspan="4">Failed to load data</td></tr>';
            }
            html += '</tbody></table>';
        }
        if (collectChart && statLeaders.length > 0) {
            chartDataMap[stat.key] = { label: stat.label, leaders: statLeaders };
        }
    }
    if (!hasAnyData) {
        html = `<div class="no-data-message"><p>No batting leader data available yet for the ${selectedSeason} season.</p><p>Check back once games have been played!</p></div>`;
    }
    target.innerHTML = html;
    if (hasAnyData) {
        const exportBtn = document.createElement('button');
        exportBtn.type = 'button';
        exportBtn.className = 'btn-export';
        exportBtn.textContent = '⬇ Export CSV';
        exportBtn.setAttribute('aria-label', `Export batting leaders as CSV`);
        exportBtn.addEventListener('click', () => exportSectionToCsv(target, `mlb-batting-${containerId.replace('batting-leaders-', '')}-${selectedSeason}.csv`));
        target.prepend(exportBtn);
        renderLeaderCharts(target, chartDataMap);
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
        fetchLeaders(basicStats, 'batting-leaders-basic');
        fetchLeaders(advancedStats, 'batting-leaders-advanced');
    });
}

initSeasonSelector();
fetchLeaders(basicStats, 'batting-leaders-basic');
fetchLeaders(advancedStats, 'batting-leaders-advanced');
