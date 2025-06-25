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
tracked_stats = ['WHIP', 'ERA', 'K/BB']
min_appearances = 3

# Combine valid CSVs
dfs = []
for file in archive_files:
    try:
        df = pd.read_csv(file)
        if df.empty or 'Name' not in df.columns:
            print(f"Skipping empty or malformed file: {file}")
            continue
        date = os.path.basename(file).replace(".csv", "")
        df = df[['Name'] + [col for col in tracked_stats if col in df.columns]].copy()
        df['Date'] = date
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        continue

if not dfs:
    print("No valid data found in archive.")
    exit()

# Combine into full dataset
all_data = pd.concat(dfs)
all_data['Date'] = pd.to_datetime(all_data['Date'])

# Create charts for each stat
for stat in tracked_stats:
    stat_df = all_data.pivot_table(index='Date', columns='Name', values=stat)
    valid_players = stat_df.count()[stat_df.count() >= min_appearances].index
    filtered = stat_df[valid_players]
    top_players = filtered.mean().sort_values().head(5).index
    trend = filtered[top_players]

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
