import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import batting_stats
from datetime import datetime
import os
from utils import save_html_table, save_standings_chart, log_error

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

try:
    # Fetch current season data
    print("Fetching batting stats for 2025 season...")
    df = batting_stats(2025)

    # Select relevant stats
    df = df[["Name", "Team", "AVG", "HR", "RBI", "OBP", "SLG", "SB", "wOBA", "wRC+", "BABIP", "ISO", "K%", "BB%"]]

    # Save CSV backup
    df.to_csv(f"{output_path}/batting_stats.csv", index=False)
    print("✓ Saved batting stats CSV backup")

    # Create charts and tables for each stat
    stats_to_plot = [
        ("AVG", "Top 10 Batters by Average", "Blues"),
        ("HR", "Top 10 Batters by Home Runs", "Reds"),
        ("RBI", "Top 10 Batters by RBI", "Greens"),
        ("OBP", "Top 10 Batters by On-Base Percentage", "Purples"),
        ("SLG", "Top 10 Batters by Slugging", "Oranges"),
        ("SB", "Top 10 Batters by Stolen Bases", "BuGn"),
        ("wOBA", "Top 10 Batters by wOBA", "viridis"),
        ("wRC+", "Top 10 Batters by wRC+", "plasma"),
        ("BABIP", "Top 10 Batters by BABIP", "magma"),
        ("ISO", "Top 10 Batters by ISO", "cool"),
        ("K%", "Lowest K% (Best Contact)", "hot"),
        ("BB%", "Top 10 Batters by Walk Rate", "winter")
    ]
    
    for stat, title, color in stats_to_plot:
        print(f"Processing {stat}...")
        # Sort in ascending order only for K%
        ascending = stat == "K%"
        top = df.sort_values(stat, ascending=ascending).head(10)
        
        # Create chart
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top, x=stat, y="Name", palette=color)
        plt.title(title)
        plt.tight_layout()
        
        # Save chart - use batting_ prefix to avoid naming conflicts
        safe_stat = stat.lower().replace("%", "_pct").replace("+", "_plus")
        chart_path = f"{output_path}/batting_{safe_stat}_chart.png"
        plt.savefig(chart_path)
        plt.close()
        
        # Create and save HTML table with dark mode support using shared utility
        table_path = f"{output_path}/batting_{safe_stat}_table.html"
        save_html_table(top, table_path)
        
        print(f"✓ Created {stat} chart and table")
    
    # Write last updated timestamp
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("✓ Batting charts and tables generated successfully!")

except Exception as e:
    print(f"Error in batting_chart.py: {e}")
    log_error(str(e), output_path)
