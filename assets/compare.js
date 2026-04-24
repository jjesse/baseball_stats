// Player comparison page - compare two players side by side
const currentYear = new Date().getFullYear();
const { createFooterUpdater, escapeHtml, fetchJsonWithRetry, initDarkModeToggle } = window.MLBUtils;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

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
            `https://statsapi.mlb.com/api/v1/people/search?names=${encodeURIComponent(query)}&sportId=1&active=true`,
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
