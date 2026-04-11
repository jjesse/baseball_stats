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

const currentYear = new Date().getFullYear();

// Set dynamic page title
const pageTitle = document.getElementById('page-title');
if (pageTitle) pageTitle.textContent = `${currentYear} MLB Batting Leaders`;
document.title = `${currentYear} MLB Batting Leaders`;

// Set footer
const footer = document.getElementById('footer');
if (footer) footer.innerHTML = `${currentYear} MLB Season &middot; Data from MLB Stats API &middot; Updated live`;

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
    let html = '';
    let hasAnyData = false;
    for (const stat of stats) {
        html += `<h2>${stat.label} Leaders</h2>`;
        for (const league of ["American League", "National League"]) {
            html += `<h3>${league}</h3>`;
            html += '<table><thead><tr><th>Rank</th><th>Player</th><th>Team</th><th>' + stat.label + '</th></tr></thead><tbody>';
            try {
                const leagueId = league === "American League" ? 103 : 104;
                const url = `https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=${stat.key}&season=${currentYear}&limit=10&statGroup=hitting&leagueId=${leagueId}`;
                const data = await fetchWithRetry(url);
                const leaders = data.leagueLeaders && data.leagueLeaders[0] && data.leagueLeaders[0].leaders ? data.leagueLeaders[0].leaders : [];
                if (leaders.length > 0) hasAnyData = true;
                if (leaders.length === 0) {
                    html += '<tr><td colspan="4">No data available yet</td></tr>';
                }
                for (const leader of leaders) {
                    html += `<tr><td>${leader.rank}</td><td>${leader.person.fullName}</td><td>${leader.team ? leader.team.name : ''}</td><td>${leader.value}</td></tr>`;
                }
            } catch (e) {
                html += '<tr><td colspan="4">Failed to load data</td></tr>';
            }
            html += '</tbody></table>';
        }
    }
    if (!hasAnyData) {
        html = `<div class="no-data-message"><p>No batting leader data available yet for the ${currentYear} season.</p><p>Check back once games have been played!</p></div>`;
    }
    document.getElementById(containerId).innerHTML = html;
    updateFooterTimestamp(currentYear);
}

setupTabs();
fetchLeaders(basicStats, 'batting-leaders-basic');
fetchLeaders(advancedStats, 'batting-leaders-advanced');
