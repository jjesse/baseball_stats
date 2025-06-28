# ⚾ MLB Stats Dashboard

This project automatically pulls **MLB pitching and batting stats** and presents them via a public GitHub Pages dashboard. It uses [pybaseball](https://github.com/jldbc/pybaseball) for data, and includes trend analysis, daily updates, and clean visualizations.

👉 **Live dashboard**: [jjesse.github.io/baseball_stats](https://jjesse.github.io/baseball_stats)

---

## 📊 Features

### 🔹 Pitching Dashboard

- Basic stats: WHIP, ERA, Strikeouts
- Advanced stats: BB, K/BB Ratio, HR/9, FIP
- Trends: WHIP, ERA, K/BB over time  
➡️ View: [`pitching.html`](docs/pitching.html)

### 🔸 Batting Dashboard

- Basic stats: AVG, HR, RBI, OBP, SLG, SB
- Advanced stats: wOBA, wRC+, BABIP, ISO, K%, BB%
- Trends: (coming soon) ISO, OBP, and wRC+ over time  
➡️ View: [`batting.html`](docs/batting.html)

---

## 🔄 How It Works

GitHub Actions power the data collection and chart generation, with two scheduled workflows:

| Action                | Description                           | Frequency       |
|-----------------------|---------------------------------------|-----------------|
| `update-pitching.yml` | Updates pitching stats, charts, trends | Daily at 12:00 UTC |
| `update-batting.yml`  | Updates batting stats, charts, trends  | Daily at 12:00 UTC |
| `update-standings.yml` | Updates standings stats, charts, trends  | Daily at 13:00 UTC |

You can also manually trigger them in the GitHub UI.

---

## 🛠 Project Structure

.
├── docs/ # GitHub Pages output (charts, tables, HTML)
│ ├── pitching.html
│ ├── batting.html
│ ├── *.png # Chart images
│ ├──*.html # Data tables
│ └── last_updated.txt
│ └── last_updated_pitching.txt # Last update timestamp for pitching
│ └── last_updated_batting.txt # Last update timestamp for batting
│ └── standings.html # Standings page
│ └── standings.png # Standings chart
│ └── standings.csv # Standings data
│ └── standings_trend.png # Standings trend chart
│ └── standings_trend.csv # Standings trend data
│ └── standings_trend.txt # Last update timestamp for standings
│ └── standings_trend_pitching.png # Standings trend chart for pitching
│ └── standings_trend_pitching.csv # Standings trend data for pitching
│ └── standings_trend_pitching.txt # Last update timestamp for pitching standings trend
│ └── standings_trend_batting.png # Standings trend chart for batting
│ └── standings_trend_batting.csv # Standings trend data for batting
│ └── standings_trend_batting.txt # Last update timestamp for batting standings trend
│ └── standings_trend_batting_pitching.png # Standings trend chart for batting
│ └── standings_trend_batting_pitching.csv # Standings trend data for batting
│ └── standings_trend_batting_pitching.txt # Last update timestamp for batting standings
│ └── standings_trend_batting_pitching.png # Standings trend chart for batting and pitching
│ └── standings_trend_batting_pitching.csv # Standings trend data for batting
│ └── standings_trend_batting_pitching.txt # Last update timestamp for batting and pitching
│ └── standings_trend_batting_pitching.png # Standings trend chart for batting and pitching
│ └── standings_trend_batting_pitching.csv # Standings trend data for batting and pitching
│ └── standings_trend_batting_pitching.txt # Last update timestamp for batting and pitching
│ └── standings_trend_batting_pitching.png # Standings trend chart for batting and pitching
│ └── standings_trend_batting_pitching.csv # Standings trend data for batting and pitching
│ └── standings_trend_batting_pitching.txt # Last update timestamp for batting and pitching
│
├── archive/ # Daily CSV snapshots for trend analysis
│
├── pitching_chart.py # Pulls and plots pitching stats
├── batting_chart.py # Pulls and plots batting stats
├── trend_pitching.py # Creates trend charts from archive/
├── trend_batting.py # Creates trend charts from archive/
│
├── .github/workflows/
│ ├── update-pitching.yml
│ └── update-batting.yml
│ └── update-standings.yml
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt # Python dependencies

---

## 🔦 Technologies Used

- [pybaseball](https://github.com/jldbc/pybaseball)
- matplotlib + seaborn
- pandas
- GitHub Actions
- GitHub Pages

---

## 📅 Data Update Schedule

All stats are refreshed **daily at 12:00 UTC** via GitHub Actions.  
Historical daily snapshots are stored in `archive/` and used to build trend charts.

---

## 📬 Contributions

This is a personal project by [@jjesse](https://github.com/jjesse).  
Suggestions, issues, and PRs are welcome!

---

## 📄 License

[MIT License](LICENSE) — free to use, modify, or share.
