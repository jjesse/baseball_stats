
// Tab logic
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    tabBtns.forEach(btn => {
        btn.onclick = () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('batting-leaders-' + btn.dataset.tab).classList.add('active');
        };
    });
}

const basicStats = [
    { key: 'avg', label: 'AVG' },
    { key: 'homeRuns', label: 'HR' },
    { key: 'rbi', label: 'RBI' },
    { key: 'hits', label: 'H' },
    { key: 'runs', label: 'R' },
    { key: 'stolenBases', label: 'SB' }
];
const advancedStats = [
    { key: 'obp', label: 'OBP' },
    { key: 'slg', label: 'SLG' },
    { key: 'ops', label: 'OPS' }
];

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
                const url = `https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=${stat.key}&season=${year}&limit=10&statGroup=hitting&leagueId=${leagueId}`;
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
fetchLeaders(basicStats, 'batting-leaders-basic');
fetchLeaders(advancedStats, 'batting-leaders-advanced');
