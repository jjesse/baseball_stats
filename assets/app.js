// Fetch MLB standings from the MLB Stats API and render them
// API docs: https://statsapi.mlb.com/api/

const standingsDiv = document.getElementById('standings');
const currentYear = new Date().getFullYear();

// Set dynamic page title
const pageTitle = document.getElementById('page-title');
if (pageTitle) pageTitle.textContent = `${currentYear} MLB Standings`;
document.title = `${currentYear} MLB Standings`;

// Set footer
const footer = document.getElementById('footer');
if (footer) footer.innerHTML = `${currentYear} MLB Season &middot; Data from MLB Stats API &middot; Updated live`;

async function fetchStandings() {
    const url = `https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=${currentYear}&standingsTypes=regularSeason`;
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        renderStandings(data);
    } catch (e) {
        standingsDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load standings.</p><p>The season may not have started yet, or the data service is temporarily unavailable. Please try again later.</p></div>';
    }
}

let currentSort = { key: null, asc: true };

function renderStandings(data) {
    if (!data.records || !Array.isArray(data.records) || data.records.length === 0) {
        standingsDiv.innerHTML = '<div class="no-data-message"><p>No standings data available yet for the ' + currentYear + ' season.</p><p>Check back once games have been played!</p></div>';
        return;
    }
    // Group by league
    const leagues = {};
    data.records.forEach(record => {
        let leagueName = record.league && record.league.name ? record.league.name : '';
        // Fallbacks for known league IDs
        if (!leagueName && record.league && record.league.id === 103) leagueName = 'American League';
        if (!leagueName && record.league && record.league.id === 104) leagueName = 'National League';
        if (!leagues[leagueName]) leagues[leagueName] = [];
        leagues[leagueName].push(record);
    });
    let html = '';
    for (const [league, divisions] of Object.entries(leagues)) {
        if (league && league !== 'undefined') {
            html += `<section class="league-section"><h2 class="league-header">${league}</h2>`;
        }
        divisions.forEach(division => {
            let divisionName = division.division && division.division.name ? division.division.name : '';
            // Fallbacks for known division IDs
            if (!divisionName && division.division && division.division.id) {
                const divisionId = division.division.id;
                if (divisionId === 201) divisionName = 'American League East';
                if (divisionId === 202) divisionName = 'American League Central';
                if (divisionId === 200) divisionName = 'American League West';
                if (divisionId === 204) divisionName = 'National League East';
                if (divisionId === 205) divisionName = 'National League Central';
                if (divisionId === 203) divisionName = 'National League West';
            }
            html += `<div class="division-section">`;
            if (divisionName && divisionName !== 'undefined') {
                html += `<h3 class="division-header">${divisionName}</h3>`;
            }
            html += `<table><thead><tr>
                <th>Team</th>
                <th class="sortable" data-sort="wins">W</th>
                <th class="sortable" data-sort="losses">L</th>
                <th class="sortable" data-sort="winningPercentage">Pct</th>
                <th>GB</th>
                <th>Streak</th>
                <th>Lg/Div Rank</th>
                <th>Magic #</th>
                <th>Status</th></tr></thead><tbody>`;
            let teamRecords = [...division.teamRecords];
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
            teamRecords.forEach(team => {
                let status = '';
                if (team.clinched) {
                    status = 'Clinched Playoff Spot';
                } else if (team.divisionChamp) {
                    status = 'Clinched Division';
                } else if (team.wildCardLeader) {
                    status = 'Wild Card Leader';
                } else if (team.hasWildcard) {
                    // Only show 'In Wild Card Race' if not eliminated
                    if (team.wildCardEliminationNumber !== 'E' && team.wildCardEliminationNumber !== 0 && team.wildCardEliminationNumber !== '0') {
                        status = 'In Wild Card Race';
                    } else {
                        status = 'Eliminated';
                    }
                }
                const logoUrl = `https://www.mlbstatic.com/team-logos/${team.team.id}.svg`;
                // Streak
                const streak = team.streak && team.streak.streakCode ? team.streak.streakCode : '';
                // League/Division Rank
                const rank = `Lg: ${team.leagueRank || ''} / Div: ${team.divisionRank || ''}`;
                // Magic Number
                const magic = team.magicNumber !== undefined && team.magicNumber !== null ? team.magicNumber : '';
                // Link to team page
                const teamLink = `team.html?teamId=${team.team.id}`;
                html += `<tr><td><a href="${teamLink}"><img src="${logoUrl}" alt="${team.team.name} logo" class="team-logo"> ${team.team.name}</a></td><td>${team.wins}</td><td>${team.losses}</td><td>${team.winningPercentage}</td><td>${team.gamesBack}</td><td>${streak}</td><td>${rank}</td><td>${magic}</td><td>${status}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            html += `</div>`;
        });
        html += `</section>`;
    }
    standingsDiv.innerHTML = html;
    document.querySelectorAll('.sortable').forEach(th => {
        th.onclick = function() {
            const key = th.getAttribute('data-sort');
            if (currentSort.key === key) {
                currentSort.asc = !currentSort.asc;
            } else {
                currentSort.key = key;
                currentSort.asc = false;
            }
            fetchStandings();
        };
    });
}

// Dark mode toggle
const darkModeToggle = document.getElementById('darkModeToggle');
if (darkModeToggle) {
    darkModeToggle.onclick = function() {
        document.body.classList.toggle('dark');
        localStorage.setItem('mlbDarkMode', document.body.classList.contains('dark'));
    };
    // On load, set dark mode if previously chosen
    if (localStorage.getItem('mlbDarkMode') === 'true') {
        document.body.classList.add('dark');
    }
}

fetchStandings();
