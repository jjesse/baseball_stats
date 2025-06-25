import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import pitching_stats
from datetime import datetime
import os

# Ensure output directory exists
os.makedirs("docs", exist_ok=True)

# Fetch current season data
df = pitching_stats(2025)

# Select relevant stats
df = df[['Name', 'Team', 'W', 'L', 'ERA', 'SO', 'BB', 'WHIP', 'K/BB', 'HR/9', 'FIP']]

# Save CSV backup (optional)
df.to_csv("docs/season_stats.csv", index=False)

# Define chart creation

def create_chart_and_table(df, stat, title, color):
    top = df.sort_values(stat, ascending=(stat in ['BB', 'ERA', 'WHIP', 'HR/9'])).head(10)

    # Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x=stat, y='Name', palette=color)
    plt.title(title)
    plt.tight_layout()
    chart_path = f"docs/{stat.lower().replace('/', '_')}_chart.png"
    plt.savefig(chart_path)
    plt.close()

    # Table HTML
    table_html = top.to_html(index=False, classes='stat-table')
    table_path = f"docs/{stat.lower().replace('/', '_')}_table.html"
    with open(table_path, "w") as f:
        f.write(table_html)


# List of stats to chart
stats_to_plot = [
    ("WHIP", "Top 10 Pitchers by WHIP", "Blues"),
    ("ERA", "Top 10 Pitchers by ERA", "Greens"),
    ("SO", "Top 10 Pitchers by Strikeouts", "Purples"),
    ("BB", "Top 10 Pitchers by Walks", "Oranges"),
    ("K/BB", "Top 10 Pitchers by K/BB Ratio", "Reds"),
    ("HR/9", "Top 10 Pitchers by HR/9", "Greys"),
    ("FIP", "Top 10 Pitchers by FIP", "BuGn"),
]

for stat, title, color in stats_to_plot:
    create_chart_and_table(df, stat, title, color)

# Write last updated timestamp
with open("docs/last_updated.txt", "w") as f:
    f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
