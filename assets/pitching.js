    // Pitching leaders with tabs for basic and advanced stats
    const basicStats = [
        { key: 'wins', label: 'W' },
        { key: 'era', label: 'ERA' },
        { key: 'strikeouts', label: 'K' },
        { key: 'saves', label: 'SV' },
        { key: 'whip', label: 'WHIP' },
        { key: 'inningsPitched', label: 'IP' },
        { key: 'opponentBattingAvg', label: 'OBA' }
    ];
    // Only use advanced stats supported by the MLB Stats API
    const advancedStats = [
        { key: 'whip', label: 'WHIP' },
        { key: 'kPer9', label: 'K/9' },
        { key: 'bbPer9', label: 'BB/9' },
        { key: 'hrPer9', label: 'HR/9' },
        { key: 'opponentBattingAvg', label: 'OBA' }
    ];

    function setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        tabBtns.forEach(btn => {
            btn.onclick = () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(tc => tc.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('pitching-leaders-' + btn.dataset.tab).classList.add('active');
            };
        });
    }

    async function fetchLeaders(stats, containerId) {
        const year = new Date().getFullYear();
        let html = '';
        for (const stat of stats) {
            html += `<h2>${stat.label} Leaders</h2>`;
            for (const league of ["American League", "National League"]) {
                html += `<h3>${league}</h3>`;
                html += '<table><thead><tr><th>Rank</th><th>Player</th><th>Team</th><th>' + stat.label + '</th></tr></thead><tbody>';
                try {
                    const leagueId = league === "American League" ? 103 : 104;
                    const url = `https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=${stat.key}&season=${year}&limit=10&statGroup=pitching&leagueId=${leagueId}`;
                    const res = await fetch(url);
                    const data = await res.json();
                    const leaders = data.leagueLeaders && data.leagueLeaders[0] && data.leagueLeaders[0].leaders ? data.leagueLeaders[0].leaders : [];
                    for (const leader of leaders) {
                        html += `<tr><td>${leader.rank}</td><td>${leader.person.fullName}</td><td>${leader.team ? leader.team.name : ''}</td><td>${leader.value}</td></tr>`;
                    }
                } catch (e) {
                    html += '<tr><td colspan="4">Failed to load data</td></tr>';
                }
                html += '</tbody></table>';
            }
        }
        document.getElementById(containerId).innerHTML = html;
    }

    setupTabs();
    fetchLeaders(basicStats, 'pitching-leaders-basic');
    fetchLeaders(advancedStats, 'pitching-leaders-advanced');
