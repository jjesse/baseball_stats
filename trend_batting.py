import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from glob import glob

sns.set(style="whitegrid")
os.makedirs("docs", exist_ok=True)

# Load historical batting data archives
archive_files = sorted(glob("archive/batting_*.csv"))
if not archive_files:
    print("No batting archive files found.")
    exit()

# Stats to track trends for
tracked_stats = ['AVG', 'OBP', 'SLG', 'wOBA', 'K%', 'BB%']
min_appearances = 3

dfs = []
for file in archive_files:
    try:
        df = pd.read_csv(file)
        if df.empty or 'Name' not in df.columns:
            print(f"Skipping empty or malformed file: {file}")
            continue
        date = os.path.basename(file).replace(".csv", "").replace("batting_", "")
        df = df[['Name'] + [col for col in tracked_stats if col in df.columns]].copy()
        df['Date'] = date
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        continue

if not dfs:
    print("No valid batting data found in archive.")
    exit()

all_data = pd.concat(dfs)
all_data['Date'] = pd.to_datetime(all_data['Date'])

for stat in tracked_stats:
    if stat not in all_data.columns:
        print(f"Stat {stat} not found in data, skipping...")
        continue
        
    stat_df = all_data.pivot_table(index='Date', columns='Name', values=stat)
    valid_players = stat_df.count()[stat_df.count() >= min_appearances].index
    filtered = stat_df[valid_players]

    # For K% lower is better, so sort ascending; others descending
    if stat == 'K%':
        top_players = filtered.mean().sort_values().head(5).index
    else:
        top_players = filtered.mean().sort_values(ascending=False).head(5).index

    trend = filtered[top_players]

    plt.figure(figsize=(12, 6))
    for player in trend.columns:
        plt.plot(trend.index, trend[player], marker='o', label=player, linewidth=2)
    plt.title(f"{stat} Trends Over Time")
    plt.xlabel("Date")
    plt.ylabel(stat)
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    filename = f"docs/batting_{stat.lower().replace('%', 'pct')}_trend.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Created trend chart: {filename}")
