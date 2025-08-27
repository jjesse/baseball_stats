import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import pitching_stats
from datetime import datetime
import os
from utils import save_html_table, save_standings_chart, log_error

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

try:
    # Fetch current season data
    df = pitching_stats(2025)

    # Select relevant stats
    df = df[
        ["Name", "Team", "W", "L", "ERA", "SO", "BB", "WHIP", "K/BB", "HR/9", "FIP"]
    ]

    # Save CSV backup (optional)
    df.to_csv(f"{output_path}/season_stats.csv", index=False)

    # Define chart creation
    def create_chart_and_table(df, stat, title, color):
        try:
            top = df.sort_values(
                stat, ascending=(stat in ["BB", "ERA", "WHIP", "HR/9"])
            ).head(10)

            # Chart
            plt.figure(figsize=(10, 6))
            sns.barplot(
                data=top, x=stat, y="Name", hue="Name", palette=color, legend=False
            )
            plt.title(title)
            plt.tight_layout()
            chart_path = f"{output_path}/{stat.lower().replace('/', '_')}_chart.png"
            plt.savefig(chart_path)
            plt.close()

            # Use shared utility to save HTML table
            save_html_table(top, stat, output_path)

            print(f"✓ Created chart and table for {stat}")

        except Exception as e:
            log_error(f"Error creating chart for {stat}: {e}")

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

    # Write last updated timestamp with proper format
    with open(f"{output_path}/last_updated_pitching.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("✓ Pitching charts and tables generated successfully!")

except Exception as e:
    log_error(f"Error in pitching_chart.py: {e}")
    # Create a minimal fallback file so the workflow doesn't fail completely
    with open(f"{output_path}/last_updated_pitching.txt", "w") as f:
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raise
