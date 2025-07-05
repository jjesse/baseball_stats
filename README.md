# MLB Stats Dashboard ⚾

A comprehensive MLB statistics dashboard that automatically tracks pitching, batting, team standings, and award predictions for the 2025 season. Features interactive charts, educational tooltips, real-time MVP & Cy Young predictions, and automated data updates via GitHub Actions.

## 🌟 Features

### 📊 Interactive Dashboard
- **Pitching Stats**: WHIP, ERA, Strikeouts, K/BB Ratio, HR/9, FIP with trends
- **Batting Stats**: AVG, HR, RBI, OBP, SLG, SB, wOBA, wRC+, BABIP, ISO, K%, BB% with trends
- **Team Standings**: Live standings by division with enhanced visualizations and league comparison
- **MVP & Cy Young Tracker**: Real-time award probability calculator based on historical voting patterns
- **Trend Analysis**: Historical performance tracking for all key metrics

### 🎨 User Experience
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Themes**: Full dark mode support with theme-aware tables and charts
- **Educational Tooltips**: Hover over "?" icons for detailed stat explanations and benchmarks
- **Performance Benchmarks**: Learn what constitutes excellent/good/average performance
- **Comprehensive Glossaries**: Complete explanation of all tracked metrics on each page
- **Professional Styling**: Consistent design language across all pages with proper centering and spacing

### 🏆 Award Predictions
- **MVP Tracking**: Real-time American League and National League MVP probability calculations
- **Cy Young Tracking**: AL and NL Cy Young Award probability calculations
- **Historical Accuracy**: Based on 20+ years of BBWAA voting patterns and statistical analysis
- **Multi-factor Analysis**: Combines individual performance, team success, and narrative factors
- **Visual Probability Charts**: Color-coded probability bars and trend visualizations
- **Daily Updates**: Probabilities adjust with each game and statistical change

### 📈 Enhanced Standings
- **Tabbed Interface**: Overview, American League, National League, and Glossary sections
- **League Leaders**: Dynamic summary cards showing AL/NL leaders and closest division races
- **Individual Division Charts**: Win comparison charts for each of the 6 divisions
- **League-Wide Visualization**: Overall wins chart with AL/NL color coding
- **Multiple Data Sources**: Robust data fetching from MLB.com, ESPN, and Baseball Reference

### 🤖 Automation
- **Daily Updates**: Batting stats, standings, and award predictions refresh automatically
- **Weekly Pitching**: Pitching stats update every Monday for comprehensive analysis
- **Trend Tracking**: Historical data archived for detailed trend analysis
- **Complete Rebuild**: Master workflow for full site regeneration
- **Error Handling**: Robust fallback systems and comprehensive logging

## 🚀 Live Demo

Visit the dashboard: [https://yourusername.github.io/baseball_stats/](https://yourusername.github.io/baseball_stats/)

## 📁 Project Structure

```
baseball_stats/
├── docs/                           # GitHub Pages site
│   ├── index.html                 # Homepage with navigation
│   ├── pitching.html              # Pitching stats dashboard with trends
│   ├── batting.html               # Batting stats dashboard with trends  
│   ├── standings.html             # Enhanced team standings with league tabs
│   ├── mvp-cy-young.html          # MVP & Cy Young award predictions
│   ├── award_predictions.json     # Real-time award prediction data
│   ├── standings_summary.json     # Standings summary statistics
│   ├── *_predictions.csv          # Award prediction CSV exports
│   ├── *.png                      # Generated charts & visualizations
│   ├── *.html                     # Generated data tables with dark mode
│   └── last_updated_*.txt         # Timestamp files for each data source
├── archive/                       # Historical data for trends
│   ├── batting_*.csv             # Daily batting archives
│   └── pitching_*.csv            # Weekly pitching archives
├── .github/workflows/            # Automation pipeline
│   ├── update-batting.yml        # Daily batting updates
│   ├── update-pitching.yml       # Weekly pitching updates
│   ├── update-standings.yml      # Daily standings with multiple sources
│   ├── update-mvp-cy-young.yml   # Daily award predictions
│   └── update-all.yml            # Master workflow (complete rebuild)
├── pitching_chart.py             # Pitching data processor with dark mode tables
├── batting_chart.py              # Batting data processor with dark mode tables
├── standings_chart.py            # Enhanced standings processor with multiple sources
├── mvp_cy_young_calculator.py    # Award prediction engine
├── create_award_charts.py        # Award visualization generator
├── trend_pitching.py             # Pitching trend analyzer (6 stats)
├── trend_batting.py              # Batting trend analyzer (6 stats)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Required packages: `pybaseball`, `pandas`, `matplotlib`, `seaborn`, `requests`, `beautifulsoup4`

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/baseball_stats.git
cd baseball_stats

# Install dependencies
pip install -r requirements.txt
# Or manually:
pip install pybaseball pandas matplotlib seaborn requests beautifulsoup4 lxml html5lib

# Generate initial data
python pitching_chart.py
python batting_chart.py
python standings_chart.py
python mvp_cy_young_calculator.py

# Serve locally (optional)
python -m http.server 8000 --directory docs
```

### GitHub Pages Deployment
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions" 
3. The workflows will automatically update the site
4. Manual triggers available for testing and debugging

## 📈 Data Sources & Metrics

### Pitching Stats
| Stat | Description | Excellence Threshold |
|------|-------------|---------------------|
| **ERA** | Earned Run Average | < 3.00 |
| **WHIP** | (Walks + Hits) / Innings | < 1.00 |
| **K/BB** | Strikeout-to-Walk Ratio | > 4.0 |
| **FIP** | Fielding Independent Pitching | < 3.20 |
| **HR/9** | Home Runs per 9 Innings | < 0.80 |
| **SO** | Total Strikeouts | > 200 (season) |

### Batting Stats
| Stat | Description | Excellence Threshold |
|------|-------------|---------------------|
| **wRC+** | Weighted Runs Created Plus | > 140 |
| **wOBA** | Weighted On-Base Average | > .400 |
| **OBP** | On-Base Percentage | > .400 |
| **SLG** | Slugging Percentage | > .550 |
| **ISO** | Isolated Power | > .250 |
| **AVG** | Batting Average | > .320 |

### Award Prediction Factors
- **Individual Performance**: Core statistical metrics and advanced analytics
- **Team Success**: Win-loss record, playoff positioning, division standings
- **Narrative Factors**: MVP/Cy Young voting history and voter preferences
- **Historical Patterns**: 20+ years of BBWAA voting data analysis

## 🔄 Update Schedule

- **Batting Stats**: Daily at 12:00 UTC
- **Pitching Stats**: Weekly (Mondays) at 3:00 UTC
- **Standings**: Daily at 13:00 UTC with multiple source fallbacks
- **MVP & Cy Young Predictions**: Daily at 14:00 UTC
- **Trend Analysis**: Generated with each respective update
- **Complete Rebuild**: Manual trigger for full site regeneration

## 🎯 Key Features Explained

### Complete Site Rebuild
The "Update All Stats (Complete Rebuild)" workflow:
- Triggers all workflows simultaneously from GitHub Actions UI
- Perfect for testing after code changes or data source issues
- Includes optional reason field for documentation and debugging
- Runs updates in parallel for faster completion
- Ideal for regenerating content after styling or structural changes

### Award Prediction System
Our MVP & Cy Young predictor features:
- **Machine Learning Approach**: Based on historical voting patterns and statistical correlations
- **Real-time Updates**: Probabilities change daily based on current performance
- **Transparent Methodology**: Complete explanation of factors and weightings
- **Visual Tracking**: Probability bars, trend charts, and race visualizations
- **League Separation**: Independent calculations for AL/NL awards
- **Narrative Integration**: Accounts for team success and voter preferences

### Enhanced Standings Dashboard
Revolutionary standings experience:
- **Multiple Data Sources**: MLB.com API, ESPN API, Baseball Reference scraping
- **Intelligent Fallbacks**: Continues working even if primary sources fail
- **Dynamic Statistics**: Real-time calculation of league leaders and division races
- **Professional Visualizations**: Individual division charts and league-wide comparisons
- **Educational Content**: Comprehensive glossary of standings terminology

### Educational Focus
Every page includes:
- **Interactive Tooltips**: Detailed explanations on hover
- **Performance Benchmarks**: What constitutes excellent/good/average performance
- **Statistical Context**: Why each metric matters and how to interpret it
- **Glossary Sections**: Comprehensive explanations for newcomers and experts

### Dark Mode Excellence
Complete dark mode implementation:
- **Theme-Aware Tables**: Data tables automatically adapt colors and contrast
- **Persistent Preferences**: User theme choice saved across sessions
- **Iframe Inheritance**: Embedded tables inherit parent page theme
- **Accessible Contrast**: Meets WCAG guidelines for readability

## 🏗️ Architecture Highlights

### Robust Data Pipeline
- **Multiple Source Redundancy**: Each data type has 2-4 fallback sources
- **Error Recovery**: Graceful degradation when sources are unavailable
- **Data Validation**: Comprehensive checks for data integrity and format
- **Archive System**: Historical data preservation for trend analysis

### Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Progressive Enhancement**: Works with and without JavaScript
- **Fast Loading**: Optimized images and efficient CSS
- **Cross-Browser**: Compatible with all modern browsers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and naming conventions
- Add educational tooltips for new statistics
- Ensure dark mode compatibility for UI changes
- Test with multiple data sources and edge cases
- Update documentation for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [pybaseball](https://github.com/jldbc/pybaseball) - Excellent Python library for baseball data
- [FanGraphs](https://www.fangraphs.com/) - Statistical definitions and benchmarks
- [Baseball Reference](https://www.baseball-reference.com/) - Historical data and context
- [MLB.com](https://www.mlb.com/) - Official statistics and standings
- [ESPN](https://www.espn.com/mlb/) - Additional data sources and verification

## 📞 Support

If you encounter any issues or have suggestions:
- Open an [Issue](https://github.com/yourusername/baseball_stats/issues)
- Check the [Discussions](https://github.com/yourusername/baseball_stats/discussions) tab
- Review automated workflow logs for debugging information
- Use the "Update All Stats" workflow to regenerate after issues

## 🚀 Recent Major Updates

- ✅ **Enhanced Standings Dashboard**: Tabbed interface, multiple data sources, dynamic statistics
- ✅ **MVP & Cy Young Predictions**: Real-time award probability calculator
- ✅ **Dark Mode Excellence**: Complete theme system with table inheritance
- ✅ **Educational Tooltips**: Comprehensive stat explanations on all pages
- ✅ **Trend Analysis**: Historical performance tracking for pitching and batting
- ✅ **Robust Data Pipeline**: Multiple fallback sources and error handling
- ✅ **Professional Styling**: Consistent design language and responsive layouts

---

**Last Updated**: January 2025 | **Status**: Actively Maintained ✅ | **Features**: Complete 🎉
