import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import batting_stats
from datetime import datetime
import os

# Ensure output directory exists
os.makedirs("docs", exist_ok=True)

# Fetch current season batting stats
df = batting_stats(2025)

# Filter players with at least 100 PA
df = df[df['PA'] >= 100]

# Compute additional stats
df['ISO'] = df['SLG'] - df['AVG']
df['K%'] = df['SO'] / df['PA']
df['BB%'] = df['BB'] / df['PA']

# Select relevant stats
df = df[['Name', 'Team', 'PA', 'AVG', 'HR', 'RBI', 'OBP', 'SLG', 'SB', 'wOBA', 'wRC+', 'BABIP', 'ISO', 'K%', 'BB%']]

# Save CSV backup
df.to_csv("docs/batting_stats.csv", index=False)

# Define chart creation
def create_chart_and_table(df, stat, title, color, ascending=False):
    top = df.sort_values(stat, ascending=ascending).head(10)

    # Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x=stat, y='Name', palette=color)
    plt.title(title)
    plt.tight_layout()
    chart_path = f"docs/batting_{stat.lower().replace('%', 'pct')}_chart.png"
    plt.savefig(chart_path)
    plt.close()

    # Table HTML
    table_html = top.to_html(index=False, classes='stat-table')
    table_path = f"docs/batting_{stat.lower().replace('%', 'pct')}_table.html"
    with open(table_path, "w") as f:
        f.write(table_html)

# List of stats to chart
stats_to_plot = [
    ("AVG", "Top 10 Batters by AVG", "Blues"),
    ("HR", "Top 10 Batters by HR", "Reds"),
    ("RBI", "Top 10 Batters by RBI", "Purples"),
    ("OBP", "Top 10 Batters by OBP", "Greens"),
    ("SLG", "Top 10 Batters by SLG", "Oranges"),
    ("SB", "Top 10 Batters by SB", "BuPu"),
    ("wOBA", "Top 10 Batters by wOBA", "YlGn"),
    ("wRC+", "Top 10 Batters by wRC+", "PuRd"),
    ("BABIP", "Top 10 Batters by BABIP", "GnBu"),
    ("ISO", "Top 10 Batters by ISO", "OrRd"),
    ("K%", "Top 10 Batters by K% (Lowest is Best)", "Greys", True),
    ("BB%", "Top 10 Batters by BB%", "PuBu")
]

for entry in stats_to_plot:
    if len(entry) == 4:
        stat, title, color, asc = entry
    else:
        stat, title, color = entry
        asc = False
    create_chart_and_table(df, stat, title, color, asc)

# Write last updated timestamp
with open("docs/last_updated_batting.txt", "w") as f:
    f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
