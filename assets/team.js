// Display team info, roster (with stats), and schedule based on teamId in URL
const teamInfoDiv = document.getElementById('team-info');
const teamRosterDiv = document.getElementById('team-roster');
const teamScheduleDiv = document.getElementById('team-schedule');
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
    const rawId = params.get('teamId');
    // Sanitize: only allow numeric team IDs
    if (rawId && /^\d+$/.test(rawId)) {
        return rawId;
    }
    return null;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
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
            const logoUrl = `https://www.mlbstatic.com/team-logos/${encodeURIComponent(teamId)}.svg`;
            const safeName = escapeHtml(team.name);
            const safeAbbr = escapeHtml(team.abbreviation);
            const safeYear = escapeHtml(String(team.firstYearOfPlay));
            teamInfoDiv.innerHTML = `<img src="${logoUrl}" alt="${safeName} logo" class="team-logo" style="width:60px;vertical-align:middle;"> <strong>${safeName}</strong> (${safeAbbr})<br>Founded: ${safeYear}`;
        }
    } catch (e) {
        teamInfoDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load team information. Please try again later.</p></div>';
    }
}

async function fetchRosterStats(teamId) {
    // Returns a map of playerId -> { hitting, pitching } season stats
    try {
        const [hitRes, pitchRes] = await Promise.all([
            fetch(`https://statsapi.mlb.com/api/v1/teams/${teamId}/stats?stats=season&season=${currentYear}&group=hitting&sportId=1`),
            fetch(`https://statsapi.mlb.com/api/v1/teams/${teamId}/stats?stats=season&season=${currentYear}&group=pitching&sportId=1`)
        ]);
        const statsMap = {};
        if (hitRes.ok) {
            const hitData = await hitRes.json();
            const splits = hitData.stats && hitData.stats[0] && hitData.stats[0].splits ? hitData.stats[0].splits : [];
            splits.forEach(s => {
                if (s.player) statsMap[s.player.id] = { hitting: s.stat };
            });
        }
        if (pitchRes.ok) {
            const pitchData = await pitchRes.json();
            const splits = pitchData.stats && pitchData.stats[0] && pitchData.stats[0].splits ? pitchData.stats[0].splits : [];
            splits.forEach(s => {
                if (s.player) {
                    if (!statsMap[s.player.id]) statsMap[s.player.id] = {};
                    statsMap[s.player.id].pitching = s.stat;
                }
            });
        }
        return statsMap;
    } catch (e) {
        return {};
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
            // Fetch per-player stats in parallel
            const statsMap = await fetchRosterStats(teamId);
            // Separate pitchers vs position players
            const pitchers = data.roster.filter(p => p.position && (p.position.type === 'Pitcher' || p.position.abbreviation === 'P'));
            const batters = data.roster.filter(p => !pitchers.includes(p));
            function buildRosterTable(players, statGroup) {
                const isPitcher = statGroup === 'pitching';
                let html = '<table><thead><tr><th>#</th><th>Name</th><th>Pos</th>';
                if (isPitcher) {
                    html += '<th>W</th><th>L</th><th>ERA</th><th>IP</th><th>K</th><th>WHIP</th>';
                } else {
                    html += '<th>AVG</th><th>HR</th><th>RBI</th><th>H</th><th>R</th><th>SB</th><th>OPS</th>';
                }
                html += '</tr></thead><tbody>';
                players.forEach(player => {
                    const pid = player.person.id;
                    const pStats = statsMap[pid];
                    const s = pStats && pStats[statGroup] ? pStats[statGroup] : null;
                    const playerUrl = `player.html?playerId=${pid}`;
                    html += `<tr><td>${escapeHtml(player.jerseyNumber || '')}</td>`;
                    html += `<td><a href="${playerUrl}">${escapeHtml(player.person.fullName)}</a></td>`;
                    html += `<td>${escapeHtml(player.position.abbreviation)}</td>`;
                    if (isPitcher) {
                        html += `<td>${s ? escapeHtml(String(s.wins !== undefined ? s.wins : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.losses !== undefined ? s.losses : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.era !== undefined ? s.era : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.inningsPitched !== undefined ? s.inningsPitched : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.strikeOuts !== undefined ? s.strikeOuts : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.whip !== undefined ? s.whip : '')) : ''}</td>`;
                    } else {
                        html += `<td>${s ? escapeHtml(String(s.avg !== undefined ? s.avg : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.homeRuns !== undefined ? s.homeRuns : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.rbi !== undefined ? s.rbi : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.hits !== undefined ? s.hits : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.runs !== undefined ? s.runs : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.stolenBases !== undefined ? s.stolenBases : '')) : ''}</td>`;
                        html += `<td>${s ? escapeHtml(String(s.ops !== undefined ? s.ops : '')) : ''}</td>`;
                    }
                    html += '</tr>';
                });
                html += '</tbody></table>';
                return html;
            }
            let html = '';
            if (batters.length > 0) {
                html += '<h3>Position Players</h3>' + buildRosterTable(batters, 'hitting');
            }
            if (pitchers.length > 0) {
                html += '<h3>Pitchers</h3>' + buildRosterTable(pitchers, 'pitching');
            }
            teamRosterDiv.innerHTML = html;
        } else {
            teamRosterDiv.innerHTML = `<div class="no-data-message"><p>No roster data available yet for the ${currentYear} season.</p></div>`;
        }
    } catch (e) {
        teamRosterDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load roster. Please try again later.</p></div>';
    }
}

async function fetchTeamSchedule(teamId) {
    const scheduleHeading = document.getElementById('schedule-heading');
    if (!teamScheduleDiv) return;
    // Fetch recent results (last 7 days) and upcoming games (next 7 days)
    const today = new Date();
    const past = new Date(today);
    past.setDate(today.getDate() - 7);
    const future = new Date(today);
    future.setDate(today.getDate() + 7);
    function fmt(d) {
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        return `${mm}/${dd}/${d.getFullYear()}`;
    }
    if (scheduleHeading) scheduleHeading.textContent = 'Schedule & Recent Results';
    try {
        const url = `https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=${teamId}&startDate=${fmt(past)}&endDate=${fmt(future)}&hydrate=linescore`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const allGames = [];
        (data.dates || []).forEach(dateObj => {
            (dateObj.games || []).forEach(g => allGames.push({ date: dateObj.date, ...g }));
        });
        if (allGames.length === 0) {
            teamScheduleDiv.innerHTML = '<div class="no-data-message"><p>No schedule data available for this period.</p></div>';
            return;
        }
        let html = '<table><thead><tr><th>Date</th><th>Opponent</th><th>Home/Away</th><th>Result/Time</th><th>Score</th></tr></thead><tbody>';
        allGames.forEach(game => {
            const isHome = game.teams.home.team.id === Number(teamId);
            const opponent = isHome ? game.teams.away.team : game.teams.home.team;
            const myTeamData = isHome ? game.teams.home : game.teams.away;
            const oppTeamData = isHome ? game.teams.away : game.teams.home;
            const oppLink = `team.html?teamId=${opponent.id}`;
            const abstract = game.status ? game.status.abstractGameState : '';
            let result = '';
            let score = '';
            if (abstract === 'Final') {
                const myScore = myTeamData.score !== undefined ? myTeamData.score : 0;
                const oppScore = oppTeamData.score !== undefined ? oppTeamData.score : 0;
                result = myScore > oppScore ? '<span class="result-win">W</span>' : '<span class="result-loss">L</span>';
                score = `${myScore}-${oppScore}`;
            } else if (abstract === 'Live') {
                result = '<span class="result-live">Live</span>';
                const myScore = myTeamData.score !== undefined ? myTeamData.score : 0;
                const oppScore = oppTeamData.score !== undefined ? oppTeamData.score : 0;
                score = `${myScore}-${oppScore}`;
            } else {
                // Scheduled
                if (game.gameDate) {
                    const gameTime = new Date(game.gameDate);
                    result = gameTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });
                } else {
                    result = escapeHtml(game.status ? game.status.detailedState : '');
                }
            }
            html += `<tr>
                <td>${escapeHtml(game.date || '')}</td>
                <td><a href="${oppLink}">${escapeHtml(opponent.name)}</a></td>
                <td>${isHome ? 'Home' : 'Away'}</td>
                <td>${result}</td>
                <td>${escapeHtml(score)}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        teamScheduleDiv.innerHTML = html;
    } catch (e) {
        teamScheduleDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load schedule. Please try again later.</p></div>';
    }
}

const teamId = getTeamIdFromUrl();
if (teamId) {
    fetchTeamInfo(teamId);
    fetchTeamRoster(teamId);
    fetchTeamSchedule(teamId);
} else {
    teamInfoDiv.innerHTML = '<p>No team selected.</p>';
    teamRosterDiv.innerHTML = '';
    if (teamScheduleDiv) teamScheduleDiv.innerHTML = '';
}
