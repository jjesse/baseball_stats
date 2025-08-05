#!/usr/bin/env python3
"""
Batting trend analyzer - Tracks batting trends over time for top players
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

def create_batting_trends():
    """Create trend charts for batting statistics"""
    try:
        # Look for archived batting data
        archive_files = sorted(glob.glob("archive/batting_*.csv"))
        
        if len(archive_files) < 2:
            print("Not enough historical data for trends (need at least 2 data points)")
            return
        
        # Load and combine historical data
        all_data = []
        for file in archive_files[-10:]:  # Last 10 data points
            try:
                df = pd.read_csv(file)
                date = file.split('_')[-1].replace('.csv', '')
                df['Date'] = date
                all_data.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
        
        if not all_data:
            print("No valid historical batting data found")
            return
        
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        
        # Stats to track trends for
        trend_stats = ['AVG', 'HR', 'RBI', 'OBP', 'SLG', 'wOBA']
        
        for stat in trend_stats:
            if stat not in combined_df.columns:
                continue
                
            try:
                # Get top 5 players by latest performance
                latest_date = combined_df['Date'].max()
                latest_data = combined_df[combined_df['Date'] == latest_date]
                
                if stat in ['K%']:  # Lower is better
                    top_players = latest_data.nsmallest(5, stat)['Name'].tolist()
                else:  # Higher is better
                    top_players = latest_data.nlargest(5, stat)['Name'].tolist()
                
                # Create trend chart
                plt.figure(figsize=(12, 8))
                
                for player in top_players:
                    player_data = combined_df[combined_df['Name'] == player].sort_values('Date')
                    if len(player_data) >= 2:
                        plt.plot(player_data['Date'], player_data[stat], marker='o', label=player, linewidth=2)
                
                plt.title(f'Batting Trends - {stat}', fontsize=16, fontweight='bold')
                plt.xlabel('Date', fontsize=12)
                plt.ylabel(stat, fontsize=12)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Save chart
                chart_path = f"{output_path}/trend_batting_{stat.lower().replace('%', '_pct')}.png"
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"✓ Created trend chart for {stat}")
                
            except Exception as e:
                print(f"Error creating trend chart for {stat}: {e}")
        
        print("✓ Batting trend analysis completed")
        
    except Exception as e:
        print(f"Error in batting trend analysis: {e}")

if __name__ == "__main__":
    create_batting_trends()
