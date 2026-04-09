// Display team info and roster based on teamId in URL
const teamInfoDiv = document.getElementById('team-info');
const teamRosterDiv = document.getElementById('team-roster');
const teamNameHeader = document.getElementById('team-name');
const currentYear = new Date().getFullYear();

// Dark mode toggle
const darkModeToggle = document.getElementById('darkModeToggle');
if (darkModeToggle) {
    darkModeToggle.onclick = function() {
        document.body.classList.toggle('dark');
        localStorage.setItem('mlbDarkMode', document.body.classList.contains('dark'));
    };
    if (localStorage.getItem('mlbDarkMode') === 'true') {
        document.body.classList.add('dark');
    }
}

// Set footer
const footer = document.getElementById('footer');
if (footer) footer.innerHTML = `${currentYear} MLB Season &middot; Data from MLB Stats API &middot; Updated live`;

function getTeamIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('teamId');
}

async function fetchTeamInfo(teamId) {
    try {
        const url = `https://statsapi.mlb.com/api/v1/teams/${teamId}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const team = data.teams && data.teams[0];
        if (team) {
            teamNameHeader.textContent = team.name;
            document.title = `${team.name} - ${currentYear} MLB`;
            const logoUrl = `https://www.mlbstatic.com/team-logos/${teamId}.svg`;
            teamInfoDiv.innerHTML = `<img src="${logoUrl}" alt="${team.name} logo" class="team-logo" style="width:60px;vertical-align:middle;"> <strong>${team.name}</strong> (${team.abbreviation})<br>Founded: ${team.firstYearOfPlay}`;
        }
    } catch (e) {
        teamInfoDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load team information. Please try again later.</p></div>';
    }
}

async function fetchTeamRoster(teamId) {
    const rosterHeading = document.getElementById('roster-heading');
    if (rosterHeading) rosterHeading.textContent = `${currentYear} Roster`;
    try {
        const url = `https://statsapi.mlb.com/api/v1/teams/${teamId}/roster/Active?season=${currentYear}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.roster && data.roster.length > 0) {
            let html = '<table><thead><tr><th>#</th><th>Name</th><th>Position</th></tr></thead><tbody>';
            for (const player of data.roster) {
                html += `<tr><td>${player.jerseyNumber || ''}</td><td>${player.person.fullName}</td><td>${player.position.abbreviation}</td></tr>`;
            }
            html += '</tbody></table>';
            teamRosterDiv.innerHTML = html;
        } else {
            teamRosterDiv.innerHTML = '<div class="no-data-message"><p>No roster data available yet for the ' + currentYear + ' season.</p></div>';
        }
    } catch (e) {
        teamRosterDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load roster. Please try again later.</p></div>';
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
