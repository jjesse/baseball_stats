import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import standings
from datetime import datetime
import os

# Ensure output directory exists
os.makedirs("docs", exist_ok=True)

# Fetch current standings
df = standings()

# Save CSV backup
df.to_csv("docs/standings.csv", index=False)

# Get unique divisions
divisions = df['Division'].unique()

# Create tables and charts per division
for division in divisions:
    div_df = df[df['Division'] == division].copy()
    div_df = div_df.sort_values('W', ascending=False)

    # Clean column order
    columns = ['Team', 'W', 'L', 'Win %', 'GB', 'Runs For', 'Runs Against', 'Division']
    div_df = div_df[[col for col in columns if col in div_df.columns]]

    # Save HTML table
    table_html = div_df.to_html(index=False, classes='stat-table')
    table_path = f"docs/standings_{division.lower().replace(' ', '_')}.html"
    with open(table_path, "w") as f:
        f.write(f"<h2>{division} Standings</h2>\n")
        f.write(table_html)

    # Create bar chart for Wins
    plt.figure(figsize=(10, 6))
    sns.barplot(data=div_df, x='W', y='Team', palette='Blues_d')
    plt.title(f"{division} - Wins")
    plt.xlabel("Wins")
    plt.ylabel("Team")
    plt.tight_layout()
    chart_path = f"docs/standings_{division.lower().replace(' ', '_')}_wins_chart.png"
    plt.savefig(chart_path)
    plt.close()

# Write last updated timestamp
with open("docs/last_updated_standings.txt", "w") as f:
    f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
