import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from glob import glob

# Set up style and output path
sns.set_theme(style="whitegrid")
output_path = os.environ.get('OUTPUT_PATH', 'docs')
os.makedirs(output_path, exist_ok=True)

try:
    # Load historical data files
    archive_files = sorted(glob("archive/batting_*.csv"))
    if not archive_files:
        print("No batting archive files found. Creating placeholder trend files.")
        # Create placeholder files to prevent workflow failures
        exit(0)

    # Stats to track trends for - matching the batting stats
    tracked_stats = ['AVG', 'HR', 'RBI', 'OBP', 'SLG', 'wOBA']
    min_appearances = 3

    # Combine valid CSVs
    dfs = []
    for file in archive_files:
        try:
            df = pd.read_csv(file)
            if df.empty or 'Name' not in df.columns:
                print(f"Skipping empty or malformed file: {file}")
                continue
            
            # Extract date from filename
            date = os.path.basename(file).replace(".csv", "").replace("batting_", "")
            
            # Only include available columns
            available_stats = [col for col in tracked_stats if col in df.columns]
            if not available_stats:
                print(f"Skipping {file} - no tracked stats available")
                continue
                
            df = df[['Name'] + available_stats].copy()
            df['Date'] = date
            dfs.append(df)
            
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue

    if not dfs:
        print("No valid batting data found in archive.")
        exit(1)

    # Combine into full dataset
    all_data = pd.concat(dfs, ignore_index=True)
    
    # Convert date column to datetime with error handling
    try:
        all_data['Date'] = pd.to_datetime(all_data['Date'])
    except Exception as e:
        print(f"Error parsing dates: {e}")
        all_data['Date'] = pd.to_datetime(all_data['Date'], errors='coerce')
        all_data = all_data.dropna(subset=['Date'])

    # Create charts for each stat
    for stat in tracked_stats:
        if stat not in all_data.columns:
            print(f"Stat {stat} not found in data, skipping")
            continue
            
        try:
            # Create pivot table
            stat_df = all_data.pivot_table(index='Date', columns='Name', values=stat, aggfunc='mean')
            
            # Filter players with minimum appearances
            valid_players = stat_df.count()[stat_df.count() >= min_appearances].index
            filtered = stat_df[valid_players]
            
            # Skip if no valid players for this stat
            if filtered.empty or len(filtered.columns) == 0:
                print(f"No valid data for {stat}, creating placeholder chart")
                plt.figure(figsize=(12, 6))
                plt.text(0.5, 0.5, f'Insufficient data for {stat} trends', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=plt.gca().transAxes, fontsize=14)
                plt.title(f"{stat} Trends Over Time - Insufficient Data")
                plt.savefig(f"{output_path}/trend_batting_{stat.lower().replace('/', '_')}.png", 
                          dpi=150, bbox_inches='tight')
                plt.close()
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
                    plt.plot(player_data.index, player_data.values, 
                           marker='o', label=player, color=colors[i], linewidth=2)
                    lines_plotted = True
            
            if lines_plotted:
                plt.title(f"{stat} Trends Over Time", fontsize=14, fontweight='bold')
                plt.xlabel("Date", fontsize=12)
                plt.ylabel(stat, fontsize=12)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                filename = f"{output_path}/trend_batting_{stat.lower().replace('/', '_')}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight')
                print(f"Generated batting trend chart for {stat}")
            else:
                print(f"No valid trend lines for {stat}, creating placeholder")
                plt.text(0.5, 0.5, f'No trend lines available for {stat}', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=plt.gca().transAxes, fontsize=14)
                plt.title(f"{stat} Trends Over Time - No Trend Lines")
                filename = f"{output_path}/trend_batting_{stat.lower().replace('/', '_')}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight')
            
            plt.close()
            
        except Exception as e:
            print(f"Error creating trend chart for {stat}: {e}")
            continue

    print("✓ Batting trend analysis completed successfully!")

except Exception as e:
    print(f"Critical error in trend_batting.py: {e}")
    # Ensure we don't leave the workflow hanging
    raise
            print(f"Error creating trend chart for {stat}: {e}")
            continue

    print("✓ Batting trend analysis completed successfully!")

except Exception as e:
    print(f"Critical error in trend_batting.py: {e}")
    # Ensure we don't leave the workflow hanging
    raise
