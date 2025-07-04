# MLB Stats Dashboard ⚾

A comprehensive MLB statistics dashboard that automatically tracks pitching, batting, and team standings for the 2025 season using the `pybaseball` library. Features interactive charts, educational tooltips, award prediction algorithms, and automated data updates via GitHub Actions.

## 🌟 Features

### 📊 Interactive Dashboard
- **Pitching Stats**: WHIP, ERA, Strikeouts, K/BB Ratio, HR/9, FIP
- **Batting Stats**: AVG, HR, RBI, OBP, SLG, SB, wOBA, wRC+, BABIP, ISO, K%, BB%
- **Team Standings**: Live standings by division with win trend charts
- **MVP & Cy Young Tracker**: Real-time award probability calculator based on historical voting patterns
- **Trend Analysis**: Historical performance tracking for all key metrics

### 🎨 User Experience
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark/Light Themes**: Full dark mode support with readable tables, user preference saved in localStorage
- **Educational Tooltips**: Hover over "?" icons for detailed stat explanations
- **Performance Benchmarks**: Learn what constitutes excellent/good/average performance
- **Comprehensive Glossary**: Complete explanation of all tracked metrics
- **Theme-Aware Tables**: Data tables automatically adapt to light/dark themes with proper contrast

### 🤖 Automation

- **Daily Updates**: Batting stats and standings refresh automatically
- **Weekly Pitching**: Pitching stats update every Monday
- **Trend Tracking**: Historical data archived for trend analysis
- **GitHub Actions**: Fully automated data pipeline with master rebuild workflow

## 🚀 Live Demo

Visit the dashboard: [https://yourusername.github.io/baseball_stats/](https://yourusername.github.io/baseball_stats/)

## 📁 Project Structure

```
baseball_stats/
├── docs/                           # GitHub Pages site
│   ├── index.html                 # Homepage with navigation
│   ├── pitching.html              # Pitching stats dashboard
│   ├── batting.html               # Batting stats dashboard
│   ├── standings.html             # Team standings
│   ├── mvp-cy-young.html          # MVP & Cy Young award predictions
│   ├── award_predictions.json     # Award prediction data
│   ├── *_predictions.csv          # Award prediction CSV files
│   ├── *.png                      # Generated charts & award race charts
│   ├── *.html                     # Generated data tables
│   └── last_updated_*.txt         # Timestamp files
├── archive/                       # Historical data for trends
│   ├── batting_*.csv             # Daily batting archives
│   └── pitching_*.csv            # Weekly pitching archives
├── .github/workflows/            # Automation
│   ├── update-batting.yml        # Daily batting updates
│   ├── update-pitching.yml       # Weekly pitching updates
│   ├── update-standings.yml      # Daily standings updates
│   ├── update-mvp-cy-young.yml   # Daily award predictions
│   └── update-all.yml            # Master workflow (complete rebuild)
├── pitching_chart.py             # Pitching data processor
├── batting_chart.py              # Batting data processor
├── standings_chart.py            # Standings data processor
├── mvp_cy_young_calculator.py    # Award prediction engine
├── create_award_charts.py        # Award visualization generator
├── trend_pitching.py             # Pitching trend analyzer
├── trend_batting.py              # Batting trend analyzer
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Required packages: `pybaseball`, `pandas`, `matplotlib`, `seaborn`

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/baseball_stats.git
cd baseball_stats

# Install dependencies
pip install pybaseball pandas matplotlib seaborn

# Generate initial data
python pitching_chart.py
python batting_chart.py
python standings_chart.py

# Serve locally (optional)
python -m http.server 8000 --directory docs
```

### GitHub Pages Deployment
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. The workflows will automatically update the site

## 📈 Data Sources & Metrics

### Pitching Stats
| Stat | Description | Good Performance |
|------|-------------|------------------|
| **ERA** | Earned Run Average | < 3.00 |
| **WHIP** | (Walks + Hits) / Innings | < 1.00 |
| **K/BB** | Strikeout-to-Walk Ratio | > 4.0 |
| **FIP** | Fielding Independent Pitching | < 3.20 |
| **HR/9** | Home Runs per 9 Innings | < 0.80 |

### Batting Stats
| Stat | Description | Good Performance |
|------|-------------|------------------|
| **wRC+** | Weighted Runs Created Plus | > 120 |
| **wOBA** | Weighted On-Base Average | > .350 |
| **OBP** | On-Base Percentage | > .360 |
| **SLG** | Slugging Percentage | > .450 |
| **ISO** | Isolated Power | > .200 |

## 🔄 Update Schedule

- **Batting Stats**: Daily at 12:00 UTC
- **Pitching Stats**: Weekly (Mondays) at 3:00 UTC  
- **Standings**: Daily at 13:00 UTC
- **MVP & Cy Young Predictions**: Daily at 14:00 UTC
- **Trend Analysis**: Generated with each update
- **Complete Rebuild**: Manual trigger via "Update All Stats" workflow

## 🎯 Key Features Explained

### Complete Site Rebuild
The "Update All Stats (Complete Rebuild)" workflow allows you to:
- Trigger all four workflows simultaneously from the GitHub Actions UI
- Perfect for testing after code changes or fixing data issues
- Includes optional reason field for documentation
- Runs all updates in parallel for faster completion
- Ideal for regenerating tables after styling fixes

### MVP & Cy Young Award Predictions
Real-time award probability calculator featuring:
- **Historical Accuracy**: Based on 20+ years of BBWAA voting patterns
- **Multi-factor Analysis**: Combines performance, team success, and narrative factors
- **League Separation**: Separate predictions for AL/NL MVP and Cy Young
- **Daily Updates**: Probabilities adjust with each game and stat change
- **Transparent Methodology**: Complete explanation of calculation factors
- **Visual Probability Tracking**: Color-coded probability bars and race charts

### Educational Tooltips
Each stat includes hover tooltips with:
- Clear explanations of what the metric measures
- Performance benchmarks (excellent/good/average/poor)
- Context about why the stat matters

### Trend Analysis
Historical tracking shows:
- Player performance over time
- Top 5 performers in each category
- Visual trends with professional charts
- Data points from daily/weekly archives

### Responsive Design

- Mobile-optimized layouts
- Consistent navigation across all pages
- Dark/light theme with user preference storage and readable table text
- Professional chart styling with proper centering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [pybaseball](https://github.com/jldbc/pybaseball) - Excellent Python library for baseball data
- [FanGraphs](https://www.fangraphs.com/) - Statistical definitions and benchmarks
- [Baseball Reference](https://www.baseball-reference.com/) - Additional statistical context

## 📞 Support

If you encounter any issues or have suggestions:
- Open an [Issue](https://github.com/yourusername/baseball_stats/issues)
- Check the [Discussions](https://github.com/yourusername/baseball_stats/discussions) tab
- Review the automated workflow logs for debugging

---

**Last Updated**: January 2025 | **Status**: Actively Maintained ✅
