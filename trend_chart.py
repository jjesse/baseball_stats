import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from glob import glob

# Set up style and output path
sns.set(style="whitegrid")
os.makedirs("docs", exist_ok=True)

# Load historical data files
archive_files = sorted(glob("archive/*.csv"))
if not archive_files:
    print("No archive files found.")
    exit()

# Stats to track
tracked_stats = ['WHIP', 'ERA', 'K/BB']  # You can add more like 'FIP', 'HR/9', etc.
min_appearances = 3  # Only chart players who appear in at least this many weeks

# Parse and combine data
dfs = []
for file in archive_files:
    date = os.path.basename(file).replace(".csv", "")
    df = pd.read_csv(file)
    df = df[['Name'] + tracked_stats].copy()
    df['Date'] = date
    dfs.append(df)

all_data = pd.concat(dfs)
all_data['Date'] = pd.to_datetime(all_data['Date'])

# Create trend charts for each stat
for stat in tracked_stats:
    stat_df = all_data.pivot_table(index='Date', columns='Name', values=stat)

    # Filter for players who appear in at least X snapshots
    valid_players = stat_df.count()[stat_df.count() >= min_appearances].index
    filtered = stat_df[valid_players]

    # Pick top 5 lowest average values for this stat (e.g., top WHIP pitchers)
    top_players = filtered.mean().sort_values().head(5).index
    trend = filtered[top_players]

    # Plot
    plt.figure(figsize=(12, 6))
    for player in trend.columns:
        plt.plot(trend.index, trend[player], marker='o', label=player)
    plt.title(f"{stat} Trends Over Time")
    plt.xlabel("Date")
    plt.ylabel(stat)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    filename = f"docs/{stat.lower().replace('/', '_')}_trend.png"
    plt.savefig(filename)
    plt.close()
