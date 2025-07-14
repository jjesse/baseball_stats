#!/usr/bin/env python3
"""
Batting trend analyzer - Tracks batting trends over time for top players
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from glob import glob
import traceback

# Set up style and output path
sns.set(style="whitegrid")
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

try:
    # Load historical data files
    archive_files = sorted(glob("archive/batting_*.csv"))
    if not archive_files:
        print("No batting archive files found.")
        exit()

    # Stats to track trends for - matching the batting stats
    tracked_stats = ["AVG", "HR", "RBI", "OBP", "SLG", "wOBA"]
    min_appearances = 3

    # Combine valid CSVs
    dfs = []
    for file in archive_files:
        try:
            df = pd.read_csv(file)
            if df.empty or "Name" not in df.columns:
                print(f"Skipping empty or malformed file: {file}")
                continue
            date = os.path.basename(file).replace(".csv", "").replace("batting_", "")
            df = df[
                ["Name"] + [col for col in tracked_stats if col in df.columns]
            ].copy()
            df["Date"] = date
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue

    if not dfs:
        print("No valid batting data found in archive.")
        exit()

    # Combine into full dataset
    all_data = pd.concat(dfs)
    all_data["Date"] = pd.to_datetime(all_data["Date"])

    # Create charts for each stat
    for stat in tracked_stats:
        try:
            stat_df = all_data.pivot_table(index="Date", columns="Name", values=stat)
            valid_players = stat_df.count()[stat_df.count() >= min_appearances].index
            filtered = stat_df[valid_players]

            # Skip if no valid players for this stat
            if filtered.empty or len(filtered.columns) == 0:
                print(f"No valid data for {stat}, skipping chart generation")
                continue

            # For batting stats, higher is generally better, so sort descending
            top_players = filtered.mean().sort_values(ascending=False).head(5).index

            trend = filtered[top_players]

            # Skip if no trend data
            if trend.empty or len(trend.columns) == 0:
                print(f"No trend data for {stat}, skipping chart generation")
                continue

            plt.figure(figsize=(12, 6))
            lines_plotted = False
            colors = plt.cm.Set1(range(len(trend.columns)))

            for i, player in enumerate(trend.columns):
                player_data = trend[player].dropna()
                if not player_data.empty and len(player_data) >= 2:  # Need at least 2 points for a trend
                    plt.plot(
                        player_data.index,
                        player_data.values,
                        marker="o",
                        label=player,
                        color=colors[i],
                        linewidth=2,
                    )
                    lines_plotted = True

            if lines_plotted:
                plt.title(f"{stat} Trends Over Time", fontsize=14, fontweight="bold")
                plt.xlabel("Date", fontsize=12)
                plt.ylabel(stat, fontsize=12)
                plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                filename = f"{output_path}/trend_batting_{stat.lower().replace('/', '_')}.png"
                plt.savefig(filename, dpi=150, bbox_inches="tight")
                print(f"Generated batting trend chart for {stat}")
            else:
                print(f"No valid trend lines for {stat}, skipping chart generation")

            plt.close()
        except Exception as e:
            print(f"Error creating trend chart for {stat}: {e}")
            traceback.print_exc()
            continue

    print("✓ Batting trend analysis completed successfully!")

except Exception as e:
    print(f"Critical error in trend_batting.py: {e}")
    # Ensure we don't leave the workflow hanging
    raise
