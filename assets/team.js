// Display team info, roster (with stats), and schedule based on teamId in URL
const teamInfoDiv = document.getElementById('team-info');
const teamRosterDiv = document.getElementById('team-roster');
const teamScheduleDiv = document.getElementById('team-schedule');
const teamNameHeader = document.getElementById('team-name');
const currentYear = new Date().getFullYear();
const {
    createFooterUpdater,
    escapeHtml,
    fetchJsonWithRetry,
    initDarkModeToggle,
    isFavorite,
    toggleFavorite
} = window.MLBUtils;

const updateFooter = createFooterUpdater(currentYear);
initDarkModeToggle();

const shareBtn = document.getElementById('shareBtn');
if (shareBtn) {
    shareBtn.addEventListener('click', () => {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(window.location.href).then(() => {
                shareBtn.textContent = '✓ Copied!';
                setTimeout(() => { shareBtn.textContent = '🔗 Share'; }, 2000);
            }).catch(() => {});
        }
    });
}

function getTeamIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const rawId = params.get('teamId');
    if (rawId && /^\d+$/.test(rawId)) {
        return rawId;
    }
    return null;
}

async function fetchTeamInfo(teamId) {
    try {
        const url = `https://statsapi.mlb.com/api/v1/teams/${teamId}`;
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
        const team = data.teams && data.teams[0];
        if (team) {
            teamNameHeader.textContent = team.name;
            document.title = `${team.name} - ${currentYear} MLB`;
            const logoUrl = `https://www.mlbstatic.com/team-logos/${encodeURIComponent(teamId)}.svg`;
            const safeName = escapeHtml(team.name);
            const safeAbbr = escapeHtml(team.abbreviation);
            const safeYear = escapeHtml(String(team.firstYearOfPlay));
            teamInfoDiv.innerHTML = `<img src="${logoUrl}" alt="${safeName} logo" class="team-logo" style="width:60px;vertical-align:middle;"> <strong>${safeName}</strong> (${safeAbbr})<br>Founded: ${safeYear}`;

            const favBtn = document.createElement('button');
            favBtn.type = 'button';
            favBtn.className = 'btn-favorite';
            const favored = isFavorite('teams', teamId);
            favBtn.textContent = favored ? '⭐ Favorited' : '☆ Add to Favorites';
            favBtn.setAttribute('aria-pressed', favored ? 'true' : 'false');
            favBtn.addEventListener('click', () => {
                const nowFav = toggleFavorite('teams', teamId, team.name);
                favBtn.textContent = nowFav ? '⭐ Favorited' : '☆ Add to Favorites';
                favBtn.setAttribute('aria-pressed', nowFav ? 'true' : 'false');
            });
            teamInfoDiv.appendChild(document.createElement('br'));
            teamInfoDiv.appendChild(favBtn);

            updateFooter(new Date());
        }
    } catch (e) {
        teamInfoDiv.innerHTML = '<div class="no-data-message"><p>⚠️ Unable to load team information. Please try again later.</p></div>';
    }
}

async function fetchRosterStats(teamId) {
    try {
        const [hitData, pitchData] = await Promise.all([
            fetchJsonWithRetry(`https://statsapi.mlb.com/api/v1/teams/${teamId}/stats?stats=season&season=${currentYear}&group=hitting&sportId=1`, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 }),
            fetchJsonWithRetry(`https://statsapi.mlb.com/api/v1/teams/${teamId}/stats?stats=season&season=${currentYear}&group=pitching&sportId=1`, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 })
        ]);

        const statsMap = {};
        const hitSplits = hitData.stats && hitData.stats[0] && hitData.stats[0].splits ? hitData.stats[0].splits : [];
        hitSplits.forEach((s) => {
            if (s.player) statsMap[s.player.id] = { hitting: s.stat };
        });

        const pitchSplits = pitchData.stats && pitchData.stats[0] && pitchData.stats[0].splits ? pitchData.stats[0].splits : [];
        pitchSplits.forEach((s) => {
            if (s.player) {
                if (!statsMap[s.player.id]) statsMap[s.player.id] = {};
                statsMap[s.player.id].pitching = s.stat;
            }
        });

        updateFooter(new Date());
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
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });

        if (data.roster && data.roster.length > 0) {
            const statsMap = await fetchRosterStats(teamId);
            const pitchers = data.roster.filter((p) => p.position && (p.position.type === 'Pitcher' || p.position.abbreviation === 'P'));
            const batters = data.roster.filter((p) => !pitchers.includes(p));

            const buildRosterTable = (players, statGroup) => {
                const isPitcher = statGroup === 'pitching';
                const caption = isPitcher ? 'Pitchers roster and season stats' : 'Position players roster and season stats';
                let html = `<table><caption class="sr-only">${caption}</caption><thead><tr><th scope="col">#</th><th scope="col">Name</th><th scope="col">Pos</th>`;
                if (isPitcher) {
                    html += '<th scope="col">W</th><th scope="col">L</th><th scope="col">ERA</th><th scope="col">IP</th><th scope="col">K</th><th scope="col">WHIP</th>';
                } else {
                    html += '<th scope="col">AVG</th><th scope="col">HR</th><th scope="col">RBI</th><th scope="col">H</th><th scope="col">R</th><th scope="col">SB</th><th scope="col">OPS</th>';
                }
                html += '</tr></thead><tbody>';

                players.forEach((player) => {
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
            };

            let html = '';
            if (batters.length > 0) {
                html += '<h3>Position Players</h3>' + buildRosterTable(batters, 'hitting');
            }
            if (pitchers.length > 0) {
                html += '<h3>Pitchers</h3>' + buildRosterTable(pitchers, 'pitching');
            }
            teamRosterDiv.innerHTML = html;
            updateFooter(new Date());
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
        const data = await fetchJsonWithRetry(url, { retries: 3, retryDelayMs: 400, cacheTtlMs: 60000 });
        const allGames = [];
        (data.dates || []).forEach((dateObj) => {
            (dateObj.games || []).forEach((g) => allGames.push({ date: dateObj.date, ...g }));
        });

        if (allGames.length === 0) {
            teamScheduleDiv.innerHTML = '<div class="no-data-message"><p>No schedule data available for this period.</p></div>';
            return;
        }

        let html = '<table><caption class="sr-only">Recent and upcoming games for selected team</caption><thead><tr><th scope="col">Date</th><th scope="col">Opponent</th><th scope="col">Home/Away</th><th scope="col">Result/Time</th><th scope="col">Score</th></tr></thead><tbody>';
        allGames.forEach((game) => {
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
            } else if (game.gameDate) {
                const gameTime = new Date(game.gameDate);
                result = gameTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });
            } else {
                result = escapeHtml(game.status ? game.status.detailedState : '');
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
        updateFooter(new Date());
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
