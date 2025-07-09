# MLB Stats Dashboard ⚾

A comprehensive MLB statistics dashboard that automatically tracks pitching, batting, team standings, and award predictions for the 2025 season. Features interactive charts, educational tooltips, real-time MVP & Cy Young predictions with accuracy tracking, and automated data updates via GitHub Actions.

## 🌟 Features

### 📊 Interactive Dashboard
- **Pitching Stats**: WHIP, ERA, Strikeouts, K/BB Ratio, HR/9, FIP with trends
- **Batting Stats**: AVG, HR, RBI, OBP, SLG, SB, wOBA, wRC+, BABIP, ISO, K%, BB% with trends
- **Team Standings**: Live standings by division with enhanced visualizations and league comparison
- **MVP & Cy Young Tracker**: Real-time award probability calculator with accuracy tracking
- **Trend Analysis**: Historical performance tracking for all key metrics

### 🎯 Award Prediction Accuracy System
- **Daily Prediction Tracking**: Saves every daily prediction with probabilities for end-of-season evaluation
- **Historical Accuracy Analysis**: Compares predictions to actual award winners once announced
- **Prediction Timeline Visualization**: Shows how predictions changed throughout the season
- **Performance Metrics**: Tracks daily accuracy rates and final prediction correctness
- **Methodology Transparency**: Complete explanation of prediction factors and success rates
- **Visual Accuracy Reports**: Charts showing prediction accuracy over time and by award category

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
- **Accuracy Validation**: End-of-season comparison to actual winners with detailed performance analysis

### 📈 Enhanced Standings
- **Tabbed Interface**: Overview, American League, National League, and Glossary sections
- **League Leaders**: Dynamic summary cards showing AL/NL leaders and closest division races
- **Individual Division Charts**: Win comparison charts for each of the 6 divisions
- **League-Wide Visualization**: Overall wins chart with AL/NL color coding
- **Multiple Data Sources**: Robust data fetching from MLB.com, ESPN, and Baseball Reference

### 🤖 Automation
- **Daily Updates**: Batting stats, standings, and award predictions refresh automatically
- **Weekly Pitching**: Pitching stats update every Monday for comprehensive analysis
- **Prediction Tracking**: Daily archiving of award predictions for accuracy analysis
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
│   ├── prediction_accuracy.html   # Award prediction accuracy dashboard
│   ├── award_predictions.json     # Real-time award prediction data
│   ├── prediction_accuracy_report.json # Prediction accuracy analysis
│   ├── actual_winners.json        # Actual award winners (updated at season end)
│   ├── prediction_history/        # Daily prediction snapshots
│   │   └── predictions_*.json     # Individual daily prediction files
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
│   ├── update-mvp-cy-young.yml   # Daily award predictions with tracking
│   ├── update-prediction-tracking.yml # Daily prediction accuracy updates
│   └── update-all.yml            # Master workflow (complete rebuild)
├── pitching_chart.py             # Pitching data processor with dark mode tables
├── batting_chart.py              # Batting data processor with dark mode tables
├── standings_chart.py            # Enhanced standings processor with multiple sources
├── mvp_cy_young_calculator.py    # Award prediction engine
├── prediction_tracker.py         # Prediction accuracy tracking system
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
python prediction_tracker.py

# Serve locally (optional)
python -m http.server 8000 --directory docs
```

### GitHub Pages Deployment
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions" 
3. The workflows will automatically update the site
4. Manual triggers available for testing and debugging

## 📊 Award Prediction Accuracy

### How We Track Accuracy
Our prediction system saves daily snapshots of award probabilities throughout the season:

- **Daily Predictions**: Every day's top predictions with probabilities
- **Historical Timeline**: Complete record of how predictions changed over time
- **Accuracy Metrics**: Percentage of days we correctly predicted the eventual winner
- **Final Accuracy**: Whether our closest-to-announcement prediction was correct

### Accuracy Evaluation (Available After Awards Announced)
Once the 2025 MLB awards are announced in November, our system will provide:

- **Daily Accuracy Rate**: What percentage of days we correctly predicted each award winner
- **Prediction Timeline Charts**: Visual representation of how predictions evolved
- **Performance Analysis**: Detailed breakdown of what factors led to correct/incorrect predictions
- **Comparative Analysis**: How our algorithm performed vs. expert predictions and betting odds

### Sample Accuracy Report
```json
{
  "al_mvp": {
    "daily_accuracy": "73.5%",
    "final_prediction": "Correct",
    "days_tracked": 150,
    "correct_predictions": 110
  },
  "methodology_insights": {
    "best_performing_factors": ["Team success", "Traditional stats"],
    "areas_for_improvement": ["Narrative factors", "Voter preferences"]
  }
}
```

## 📈 Data Sources & Metrics

### Award Prediction Factors
- **Individual Performance**: Core statistical metrics and advanced analytics
- **Team Success**: Win-loss record, playoff positioning, division standings
- **Narrative Factors**: MVP/Cy Young voting history and voter preferences
- **Historical Patterns**: 20+ years of BBWAA voting data analysis

### Accuracy Tracking Methodology
1. **Daily Snapshots**: Save top 10 predictions with probabilities each day
2. **Winner Comparison**: Compare predictions to actual award winners
3. **Timeline Analysis**: Track how predictions changed throughout season
4. **Performance Metrics**: Calculate accuracy rates and success patterns

## 🔄 Update Schedule

- **Batting Stats**: Daily at 12:00 UTC
- **Pitching Stats**: Weekly (Mondays) at 3:00 UTC
- **Standings**: Daily at 13:00 UTC with multiple source fallbacks
- **MVP & Cy Young Predictions**: Daily at 14:00 UTC
- **Prediction Accuracy Tracking**: Daily at 15:00 UTC
- **Trend Analysis**: Generated with each respective update
- **Complete Rebuild**: Manual trigger for full site regeneration

## 🎯 Key Features Explained

### Award Prediction Accuracy System
Our comprehensive accuracy tracking includes:
- **Transparent Methodology**: Complete explanation of prediction algorithms
- **Historical Validation**: End-of-season comparison to actual winners
- **Performance Insights**: Analysis of what factors work best for each award
- **Continuous Improvement**: Use accuracy data to refine future predictions
- **Visual Reporting**: Charts and graphs showing prediction performance over time

### Complete Site Rebuild
The "Update All Stats (Complete Rebuild)" workflow:
- Triggers all workflows simultaneously from GitHub Actions UI
- Includes the new prediction tracking workflow
- Perfect for testing after code changes or data source issues
- Includes optional reason field for documentation and debugging
- Runs updates in parallel for faster completion

## 🏗️ Architecture Highlights

### Prediction Tracking Pipeline
- **Daily Archiving**: Automatic saving of predictions with timestamps
- **Accuracy Calculation**: Real-time evaluation against actual winners
- **Visualization Generation**: Automated chart creation for accuracy reports
- **Historical Analysis**: Trend tracking for prediction performance improvement

### Robust Data Pipeline
- **Multiple Source Redundancy**: Each data type has 2-4 fallback sources
- **Error Recovery**: Graceful degradation when sources are unavailable
- **Data Validation**: Comprehensive checks for data integrity and format
- **Archive System**: Historical data preservation for trend analysis

## 🤝 Contributing

### Development Guidelines
- Follow existing code style and naming conventions
- Add educational tooltips for new statistics
- Ensure dark mode compatibility for UI changes
- Test prediction accuracy tracking with sample data
- Update documentation for new features

## 🚀 Recent Major Updates

- ✅ **Award Prediction Accuracy Tracking**: Complete system for evaluating prediction performance
- ✅ **Daily Prediction Archiving**: Automatic saving of predictions for end-of-season analysis
- ✅ **Enhanced Prediction Workflows**: Integrated tracking into existing MVP/Cy Young updates
- ✅ **Accuracy Visualization**: Charts and reports showing prediction performance over time
- ✅ **Transparent Methodology**: Complete explanation of how accuracy is measured and reported

---

**Last Updated**: January 2025 | **Status**: Actively Maintained ✅ | **Features**: Complete with Accuracy Tracking 🎯
