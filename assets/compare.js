/* global Chart */
// Player comparison page - compare two players side by side
const currentYear = new Date().getFullYear();
const { createFooterUpdater, escapeHtml, fetchJsonWithRetry, initDarkModeToggle } = window.MLBUtils;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

const comparePlayerData = { 1: null, 2: null };
let compareCharts = [];

function getChartTheme() {
    const s = getComputedStyle(document.body);
    return {
        text: s.getPropertyValue('--clr-text').trim() || '#1a2035',
        muted: s.getPropertyValue('--clr-text-muted').trim() || '#64748b',
        grid: s.getPropertyValue('--clr-border').trim() || '#d1dce8'
    };
}

function renderCompareCharts() {
    if (typeof Chart === 'undefined') return;
    const d1 = comparePlayerData[1];
    const d2 = comparePlayerData[2];
    if (!d1 || !d2) return;

    const section = document.getElementById('compare-chart-section');
    if (!section) return;

    // Destroy old charts
    compareCharts.forEach(c => c.destroy());
    compareCharts = [];
    section.innerHTML = '';
    section.hidden = false;

    const statGroup = (d1.statGroup === 'pitching' && d2.statGroup === 'pitching') ? 'pitching' : 'hitting';
    const theme = getChartTheme();

    const getVal = (stats, key) => {
        if (!stats || stats.length === 0) return 0;
        const s = stats[0].stat;
        return parseFloat(s[key]) || 0;
    };

    let chartConfigs;
    if (statGroup === 'hitting') {
        chartConfigs = [
            {
                title: `${currentYear} Rate Stats`,
                keys:   ['avg', 'obp', 'slg', 'ops'],
                labels: ['AVG', 'OBP', 'SLG', 'OPS']
            },
            {
                title: `${currentYear} Counting Stats`,
                keys:   ['homeRuns', 'rbi', 'runs', 'stolenBases'],
                labels: ['HR', 'RBI', 'R', 'SB']
            }
        ];
    } else {
        chartConfigs = [
            {
                title: `${currentYear} Rate Stats`,
                keys:   ['era', 'whip'],
                labels: ['ERA', 'WHIP']
            },
            {
                title: `${currentYear} Counting Stats`,
                keys:   ['wins', 'strikeOuts', 'saves'],
                labels: ['W', 'K', 'SV']
            }
        ];
    }

    const heading = document.createElement('h2');
    heading.textContent = 'Season Comparison';
    section.appendChild(heading);

    const grid = document.createElement('div');
    grid.className = 'compare-charts-grid';
    section.appendChild(grid);

    chartConfigs.forEach(({ title, keys, labels }) => {
        const d1Values = keys.map(k => getVal(d1.seasonStats, k));
        const d2Values = keys.map(k => getVal(d2.seasonStats, k));

        const card = document.createElement('div');
        card.className = 'chart-card';
        const titleEl = document.createElement('p');
        titleEl.className = 'chart-card-title';
        titleEl.textContent = title;
        const wrap = document.createElement('div');
        wrap.className = 'compare-chart-wrap';
        const canvas = document.createElement('canvas');
        canvas.setAttribute('aria-label', `${title} comparison bar chart`);
        canvas.setAttribute('role', 'img');
        wrap.appendChild(canvas);
        card.append(titleEl, wrap);
        grid.appendChild(card);

        const chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: d1.name,
                        data: d1Values,
                        backgroundColor: 'rgba(4,30,66,0.82)',
                        borderRadius: 3
                    },
                    {
                        label: d2.name,
                        data: d2Values,
                        backgroundColor: 'rgba(213,0,50,0.82)',
                        borderRadius: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { labels: { color: theme.text, font: { size: 12 } } }
                },
                scales: {
                    x: {
                        ticks: { color: theme.text, font: { size: 11 } },
                        grid: { color: theme.grid }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: theme.text, font: { size: 11 } },
                        grid: { color: theme.grid }
                    }
                }
            }
        });
        compareCharts.push(chart);
    });
}

function getParamsFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const p1 = params.get('p1');
    const p2 = params.get('p2');
    return {
        p1: p1 && /^\d+$/.test(p1) ? p1 : null,
        p2: p2 && /^\d+$/.test(p2) ? p2 : null
    };
}

function updateUrlParams(p1, p2) {
    const url = new URL(window.location.href);
    if (p1) url.searchParams.set('p1', p1); else url.searchParams.delete('p1');
    if (p2) url.searchParams.set('p2', p2); else url.searchParams.delete('p2');
    window.history.replaceState({}, '', url);
}

async function searchPlayers(query, slotNum) {
    const resultsDiv = document.getElementById(`search-results-${slotNum}`);
    if (!resultsDiv) return;
    if (query.length < 2) {
        resultsDiv.innerHTML = '<span>Enter at least 2 characters.</span>';
        return;
    }
    resultsDiv.innerHTML = '<span>Searching…</span>';
    try {
        const data = await fetchJsonWithRetry(
            `https://statsapi.mlb.com/api/v1/people/search?names=${encodeURIComponent(query)}&sportId=1`,
            { retries: 2, retryDelayMs: 400, cacheTtlMs: 15000 }
        );
        const people = data.people || [];
        if (people.length === 0) {
            resultsDiv.innerHTML = '<span>No players found.</span>';
            return;
        }
        let html = '';
        people.slice(0, 10).forEach((p) => {
            const pos = p.primaryPosition ? escapeHtml(p.primaryPosition.abbreviation || '') : '';
            const team = p.currentTeam ? escapeHtml(p.currentTeam.name || '') : 'Free Agent';
            html += `<a href="#" data-player-id="${p.id}" data-player-name="${escapeHtml(p.fullName)}">${escapeHtml(p.fullName)} (${pos} — ${team})</a>`;
        });
        resultsDiv.innerHTML = html;

        resultsDiv.querySelectorAll('a[data-player-id]').forEach((link) => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pid = link.getAttribute('data-player-id');
                const pname = link.getAttribute('data-player-name');
                resultsDiv.innerHTML = '';
                const input = document.getElementById(`search-input-${slotNum}`);
                if (input) input.value = pname;
                loadPlayerSlot(slotNum, pid);
            });
        });
    } catch (err) {
        resultsDiv.innerHTML = '<span>Search failed. Please try again.</span>';
    }
}

function buildBioHtml(person) {
    const teamName = person.currentTeam ? escapeHtml(person.currentTeam.name) : 'N/A';
    const teamId = person.currentTeam ? person.currentTeam.id : null;
    const teamLink = teamId ? `<a href="team.html?teamId=${teamId}">${teamName}</a>` : teamName;
    const pos = person.primaryPosition ? escapeHtml(person.primaryPosition.abbreviation) : 'N/A';
    const bats = escapeHtml(person.batSide ? person.batSide.description : 'N/A');
    const throws = escapeHtml(person.pitchHand ? person.pitchHand.description : 'N/A');
    const dob = escapeHtml(person.birthDate || 'N/A');
    return `<div class="player-bio">
        <p><strong>Team:</strong> ${teamLink}</p>
        <p><strong>Position:</strong> ${pos}</p>
        <p><strong>Bats/Throws:</strong> ${bats}/${throws}</p>
        <p><strong>Born:</strong> ${dob}</p>
    </div>`;
}

function buildStatsTable(stats, statGroup) {
    if (!stats || stats.length === 0) return '<p class="no-data-message">No stats available.</p>';
    let keys;
    if (statGroup === 'hitting') {
        keys = ['season', 'gamesPlayed', 'atBats', 'hits', 'homeRuns', 'rbi', 'avg', 'obp', 'slg', 'ops'];
    } else {
        keys = ['season', 'gamesPlayed', 'wins', 'losses', 'era', 'inningsPitched', 'strikeOuts', 'whip'];
    }
    const headers = {
        season: 'Season', gamesPlayed: 'G', atBats: 'AB', hits: 'H', homeRuns: 'HR',
        rbi: 'RBI', avg: 'AVG', obp: 'OBP', slg: 'SLG', ops: 'OPS',
        wins: 'W', losses: 'L', era: 'ERA', inningsPitched: 'IP', strikeOuts: 'K', whip: 'WHIP'
    };
    let html = '<table><thead><tr>';
    keys.forEach((k) => { html += `<th scope="col">${headers[k] || k}</th>`; });
    html += '</tr></thead><tbody>';
    stats.forEach((row) => {
        const s = row.stat;
        const seasonLabel = row.season || '';
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

async function loadPlayerSlot(slotNum, playerId) {
    const dataDiv = document.getElementById(`player-data-${slotNum}`);
    const slotHeading = document.querySelector(`#compare-slot-${slotNum} h2`);
    if (!dataDiv) return;

    dataDiv.innerHTML = '<div class="loading-indicator" role="status" aria-live="polite"><span class="loading-spinner" aria-hidden="true"></span><span>Loading player…</span></div>';

    const params = getParamsFromUrl();
    const newParams = { ...params };
    newParams[`p${slotNum}`] = playerId;
    updateUrlParams(newParams.p1, newParams.p2);

    try {
        const personData = await fetchJsonWithRetry(
            `https://statsapi.mlb.com/api/v1/people/${playerId}?hydrate=currentTeam`,
            { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 }
        );
        const person = personData.people && personData.people[0];
        if (!person) {
            dataDiv.innerHTML = '<div class="no-data-message"><p>Player not found.</p></div>';
            return;
        }
        if (slotHeading) slotHeading.textContent = escapeHtml(person.fullName);

        let statGroup = 'hitting';
        if (person.primaryPosition) {
            const pos = person.primaryPosition.abbreviation;
            if (pos === 'P' || pos === 'SP' || pos === 'RP' || pos === 'CL') statGroup = 'pitching';
        }

        const [careerData, seasonData] = await Promise.all([
            fetchJsonWithRetry(
                `https://statsapi.mlb.com/api/v1/people/${playerId}/stats?stats=yearByYear&group=${statGroup}&sportId=1`,
                { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 }
            ),
            fetchJsonWithRetry(
                `https://statsapi.mlb.com/api/v1/people/${playerId}/stats?stats=season&season=${currentYear}&group=${statGroup}&sportId=1`,
                { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 }
            )
        ]);

        const careerStats = careerData.stats && careerData.stats[0] && careerData.stats[0].splits ? careerData.stats[0].splits : [];
        const seasonStats = seasonData.stats && seasonData.stats[0] && seasonData.stats[0].splits ? seasonData.stats[0].splits : [];

        let html = buildBioHtml(person);
        html += `<h3>${currentYear} Season Stats</h3>`;
        html += buildStatsTable(seasonStats, statGroup);
        html += '<h3>Career Stats (Year by Year)</h3>';
        html += buildStatsTable(careerStats, statGroup);

        dataDiv.innerHTML = html;
        updateFooter(new Date());

        // Store data for comparison chart and re-render if both slots are filled
        comparePlayerData[slotNum] = { name: person.fullName, statGroup, seasonStats };
        renderCompareCharts();
    } catch (err) {
        dataDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load player data. Please try again later.</p></div>';
    }
}

function setupSlot(slotNum) {
    const input = document.getElementById(`search-input-${slotNum}`);
    const btn = document.getElementById(`search-btn-${slotNum}`);
    if (!input || !btn) return;

    btn.addEventListener('click', () => searchPlayers(input.value.trim(), slotNum));
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') searchPlayers(input.value.trim(), slotNum);
    });
}

function init() {
    setupSlot(1);
    setupSlot(2);

    const { p1, p2 } = getParamsFromUrl();
    if (p1) loadPlayerSlot(1, p1);
    if (p2) loadPlayerSlot(2, p2);
}

init();
