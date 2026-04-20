// Player profile page - shows bio, career stats, season stats, and splits
const playerNameHeader = document.getElementById('player-name');
const playerInfoDiv = document.getElementById('player-info');
const currentYear = new Date().getFullYear();
const { createFooterUpdater, escapeHtml, fetchJsonWithRetry, initDarkModeToggle, setupAccessibleTabs } = window.MLBUtils;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

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
            careerDiv.innerHTML = '<div class="no-data-message"><p>No career stats available.</p></div>';
        } else {
            careerDiv.innerHTML = '<h2>Career Stats (Year by Year)</h2>' + buildStatsTable(stats, statGroup);
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
            seasonDiv.innerHTML = `<h2>${currentYear} Season Stats</h2>` + buildStatsTable(stats, statGroup);
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
            splitsDiv.innerHTML = `<div class="no-data-message"><p>No ${currentYear} splits data available yet.</p></div>`;
        } else {
            let html = `<h2>${currentYear} Splits</h2><table><thead><tr><th scope="col">Split</th>`;
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
        }
        updateFooter(new Date());
    } catch (e) {
        splitsDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load splits. Please try again later.</p></div>';
    }
}

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
    fetchCareerStats(playerId, statGroup);
    fetchSeasonStats(playerId, statGroup);
    fetchSplits(playerId, statGroup);
}

init();
