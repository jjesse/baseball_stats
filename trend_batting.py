#!/usr/bin/env python3
"""
Batting trend analyzer - Tracks batting trends over time for top players
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import glob

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

def create_batting_trends():
    """Create trend charts for key batting statistics"""
    try:
        # Load archived batting data
        archive_files = sorted(glob.glob("archive/batting_*.csv"))
        
        if len(archive_files) < 2:
            print("Not enough historical data for trend analysis")
            return
        
        # Define stats to track
        stats_to_track = ["AVG", "HR", "RBI", "OBP", "SLG", "wOBA"]
        
        for stat in stats_to_track:
            try:
                # Initialize data storage
                trend_data = {}
                dates = []
                
                for file_path in archive_files:
                    try:
                        # Extract date from filename
                        filename = os.path.basename(file_path)
                        date_str = filename.replace("batting_", "").replace(".csv", "")
                        dates.append(pd.to_datetime(date_str))
                        
                        # Load data
                        df = pd.read_csv(file_path)
                        
                        if stat in df.columns:
                            # Get top 5 players for this stat
                            top_players = df.nlargest(5, stat)
                            
                            # Store data for each player
                            for _, player in top_players.iterrows():
                                player_name = player["Name"]
                                if player_name not in trend_data:
                                    trend_data[player_name] = []
                                trend_data[player_name].append(player[stat])
                        
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        continue
                
                if not trend_data or len(dates) < 2:
                    print(f"Insufficient data for {stat} trends")
                    continue
                
                # Create trend chart
                plt.figure(figsize=(12, 8))
                
                lines_plotted = False
                for player_name, values in trend_data.items():
                    if len(values) == len(dates):
                        plt.plot(dates, values, marker='o', label=player_name, linewidth=2)
                        lines_plotted = True
                
                if lines_plotted:
                    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                
                plt.title(f"{stat} Trends - Top Performers Over Time", fontsize=14, fontweight='bold')
                plt.xlabel("Date", fontsize=12)
                plt.ylabel(stat, fontsize=12)
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                # Save chart
                chart_path = f"{output_path}/trend_batting_{stat.lower()}.png"
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"✓ Created trend chart for {stat}")
                
            except Exception as e:
                print(f"Error creating trend chart for {stat}: {e}")
                continue
        
        print("✓ Batting trend analysis completed!")
        
    except Exception as e:
        print(f"Error in batting trend analysis: {e}")

if __name__ == "__main__":
    create_batting_trends()
        # Customize the chart
        plt.title(f'{title} Trends - Top 5 Players', fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel(stat, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart
        filename = f"{output_path}/trend_batting_{stat.lower().replace('/', '_')}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created trend chart for {stat}")
        
    except Exception as e:
        print(f"Error creating trend chart for {stat}: {e}")

if __name__ == "__main__":
    create_batting_trends()
