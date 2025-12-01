// 2025 Season Archive - Team Page
// Display team info and roster based on teamId in URL
const teamInfoDiv = document.getElementById('team-info');
const teamRosterDiv = document.getElementById('team-roster');
const teamNameHeader = document.getElementById('team-name');

function getTeamIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('teamId');
}

async function fetchTeamInfo(teamId) {
    const url = `https://statsapi.mlb.com/api/v1/teams/${teamId}`;
    const res = await fetch(url);
    const data = await res.json();
    const team = data.teams && data.teams[0];
    if (team) {
        teamNameHeader.textContent = team.name + ' - 2025 Season';
        const logoUrl = `https://www.mlbstatic.com/team-logos/${teamId}.svg`;
        teamInfoDiv.innerHTML = `<img src="${logoUrl}" alt="${team.name} logo" class="team-logo" style="width:60px;vertical-align:middle;"> <strong>${team.name}</strong> (${team.abbreviation})<br>Founded: ${team.firstYearOfPlay}`;
    }
}

async function fetchTeamRoster(teamId) {
    // Hardcoded 2025 for archive - fetch roster from 2025 season
    const url = `https://statsapi.mlb.com/api/v1/teams/${teamId}/roster?season=2025`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.roster && data.roster.length > 0) {
        let html = '<table><thead><tr><th>#</th><th>Name</th><th>Position</th></tr></thead><tbody>';
        for (const player of data.roster) {
            html += `<tr><td>${player.jerseyNumber || ''}</td><td>${player.person.fullName}</td><td>${player.position.abbreviation}</td></tr>`;
        }
        html += '</tbody></table>';
        teamRosterDiv.innerHTML = html;
    } else {
        teamRosterDiv.innerHTML = '<p>No roster data available.</p>';
    }
}

const teamId = getTeamIdFromUrl();
if (teamId) {
    fetchTeamInfo(teamId);
    fetchTeamRoster(teamId);
} else {
    teamInfoDiv.innerHTML = '<p>No team selected.</p>';
    teamRosterDiv.innerHTML = '';
}
