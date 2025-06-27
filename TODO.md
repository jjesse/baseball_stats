# 📋 MLB Stats Dashboard – To-Do List

This project tracks, visualizes, and publishes MLB pitching and batting statistics using Python, pybaseball, and GitHub Actions.

---

## ✅ Completed Tasks

- ✅ Split `index.html` into `index.html`, `pitching.html`, and `batting.html`
- ✅ Created `pitching_chart.py` and `batting_chart.py` scripts
- ✅ Built trend tracking scripts: `trend_pitching.py` and `trend_batting.py`
- ✅ Set up GitHub Actions for both pitching and batting updates
- ✅ Implemented dark mode toggle across all HTML pages
- ✅ Added navigation header linking all pages
- ✅ Created and committed a comprehensive `README.md`

---

## 📌 Current Outstanding Tasks

### 🔁 GitHub Actions / Automation

- [ ] **Update `update-pitching.yml`**
  - Ensure it commits only `last_updated_pitching.txt`, `season_stats.csv`, and pitching trends.
- [ ] **Update `update-batting.yml`**
  - Ensure it commits only `last_updated_batting.txt`, `batting_stats.csv`, and batting trends.
- [ ] *(Optional)* Add error handling if `pybaseball` fails (e.g., API rate limits, connectivity issues).

---

### 📊 Batting Dashboard Improvements

- [ ] **Trends**
  - Confirm `trend_batting.py` charts are generated consistently.
  - Verify images appear in the **Trends** tab of `batting.html`.

---

### 🧪 Testing & Validation

- [ ] Test GitHub Actions workflows on the `main` branch now that everything is merged.
- [ ] Verify dark mode toggle and tab switching work properly on both mobile and desktop.
- [ ] Confirm `.csv` archives in `/archive/` update correctly for pitching and batting.

---

### 📦 Future Features & Enhancements

- [ ] Add team-level or player profile drill-downs (e.g., individual player pages).
- [ ] Enable season-over-season comparisons (e.g., 2024 vs. 2025).
- [ ] Add percentile ranks or heatmaps to visualize advanced stats.
- [ ] Make HTML tables filterable and sortable.
- [ ] Allow users to download `.csv` files from the dashboard.
- [ ] Build an interactive dashboard version in Streamlit or Plotly Dash.

---

*Feel free to edit this file as progress is made!*
