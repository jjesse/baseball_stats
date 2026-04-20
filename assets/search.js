// Global search - find teams or players by name
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const searchResultsDiv = document.getElementById('search-results');
const currentYear = new Date().getFullYear();
const { createFooterUpdater, escapeHtml, fetchJsonWithRetry, initDarkModeToggle } = window.MLBUtils;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

let allTeams = [];

async function loadTeams() {
    try {
        const data = await fetchJsonWithRetry(`https://statsapi.mlb.com/api/v1/teams?sportId=1&season=${currentYear}`, { retries: 3, retryDelayMs: 400, cacheTtlMs: 300000 });
        allTeams = data.teams || [];
        updateFooter(new Date());
    } catch (e) {
        allTeams = [];
    }
}

async function searchPlayers(query) {
    try {
        const data = await fetchJsonWithRetry(`https://statsapi.mlb.com/api/v1/people/search?names=${encodeURIComponent(query)}&sportId=1&active=true`, { retries: 3, retryDelayMs: 400, cacheTtlMs: 15000 });
        updateFooter(new Date());
        return data.people || [];
    } catch (e) {
        return [];
    }
}

async function performSearch() {
    const query = searchInput.value.trim();
    if (query.length < 2) {
        searchResultsDiv.innerHTML = '<p>Please enter at least 2 characters to search.</p>';
        return;
    }
    searchResultsDiv.innerHTML = '<div class="loading-indicator" role="status" aria-live="polite"><span class="loading-spinner" aria-hidden="true"></span><span>Searching…</span></div>';
    const lower = query.toLowerCase();

    const matchedTeams = allTeams.filter((t) =>
        (t.name && t.name.toLowerCase().includes(lower)) ||
        (t.abbreviation && t.abbreviation.toLowerCase().includes(lower)) ||
        (t.locationName && t.locationName.toLowerCase().includes(lower)) ||
        (t.teamName && t.teamName.toLowerCase().includes(lower))
    );
    const matchedPlayers = await searchPlayers(query);

    if (matchedTeams.length === 0 && matchedPlayers.length === 0) {
        searchResultsDiv.innerHTML = `<div class="no-data-message"><p>No results found for "<strong>${escapeHtml(query)}</strong>".</p></div>`;
        return;
    }

    let html = '';
    if (matchedTeams.length > 0) {
        html += '<h2>Teams</h2><table><thead><tr><th scope="col">Logo</th><th scope="col">Team</th><th scope="col">League</th><th scope="col">Division</th></tr></thead><tbody>';
        matchedTeams.forEach((t) => {
            const logoUrl = `https://www.mlbstatic.com/team-logos/${t.id}.svg`;
            const teamLink = `team.html?teamId=${t.id}`;
            const league = t.league ? escapeHtml(t.league.name || '') : '';
            const division = t.division ? escapeHtml(t.division.name || '') : '';
            html += `<tr>
                <td><img src="${logoUrl}" alt="${escapeHtml(t.name)} logo" class="team-logo"></td>
                <td><a href="${teamLink}">${escapeHtml(t.name)}</a></td>
                <td>${league}</td>
                <td>${division}</td>
            </tr>`;
        });
        html += '</tbody></table>';
    }

    if (matchedPlayers.length > 0) {
        html += '<h2>Players</h2><table><thead><tr><th scope="col">Name</th><th scope="col">Position</th><th scope="col">Team</th></tr></thead><tbody>';
        matchedPlayers.slice(0, 20).forEach((p) => {
            const playerLink = `player.html?playerId=${p.id}`;
            const pos = p.primaryPosition ? escapeHtml(p.primaryPosition.abbreviation || '') : '';
            const teamName = p.currentTeam ? escapeHtml(p.currentTeam.name || '') : '';
            const teamId = p.currentTeam ? p.currentTeam.id : null;
            const teamCell = teamId ? `<a href="team.html?teamId=${teamId}">${teamName}</a>` : teamName;
            html += `<tr>
                <td><a href="${playerLink}">${escapeHtml(p.fullName)}</a></td>
                <td>${pos}</td>
                <td>${teamCell}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        if (matchedPlayers.length > 20) {
            html += `<p class="search-more">Showing top 20 of ${matchedPlayers.length} player results. Refine your search for better results.</p>`;
        }
    }
    searchResultsDiv.innerHTML = html;
}

searchBtn.onclick = performSearch;
searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') performSearch();
});

const params = new URLSearchParams(window.location.search);
const urlQuery = params.get('q');
if (urlQuery) {
    searchInput.value = urlQuery;
    loadTeams().then(performSearch);
} else {
    loadTeams();
}
