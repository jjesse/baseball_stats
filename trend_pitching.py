import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import glob

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

def create_pitching_trends():
    """Create trend charts for key pitching statistics"""
    
    try:
        # Get all archived pitching files
        archive_files = sorted(glob.glob("archive/pitching_*.csv"))
        
        if len(archive_files) < 2:
            print("Not enough historical data for trends (need at least 2 files)")
            return
        
        # Read all files and combine
        all_data = []
        for file in archive_files:
            try:
                df = pd.read_csv(file)
                # Extract date from filename
                date_str = file.split('_')[-1].replace('.csv', '')
                df['Date'] = pd.to_datetime(date_str)
                all_data.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
        
        if not all_data:
            print("No valid archive data found")
            return
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Stats to track
        stats_to_track = [
            ('ERA', 'Earned Run Average', 'lower_better'),
            ('WHIP', 'WHIP (Walks + Hits per IP)', 'lower_better'),
            ('SO', 'Strikeouts', 'higher_better'),
            ('K/BB', 'Strikeout to Walk Ratio', 'higher_better'),
            ('HR/9', 'Home Runs per 9 Innings', 'lower_better'),
            ('FIP', 'Fielding Independent Pitching', 'lower_better')
        ]
        
        for stat, title, direction in stats_to_track:
            if stat not in combined_df.columns:
                print(f"Stat {stat} not found in data")
                continue
                
            create_trend_chart(combined_df, stat, title, direction)
        
        print("✓ Pitching trend charts created successfully!")
        
    except Exception as e:
        print(f"Error creating pitching trends: {e}")

def create_trend_chart(df, stat, title, direction):
    """Create a trend chart for a specific statistic"""
    
    try:
        # Get top 5 players by latest values
        latest_date = df['Date'].max()
        latest_data = df[df['Date'] == latest_date]
        
        if direction == 'lower_better':
            top_players = latest_data.nsmallest(5, stat)['Name'].tolist()
        else:
            top_players = latest_data.nlargest(5, stat)['Name'].tolist()
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Track if we plotted any lines
        lines_plotted = False
        
        # Plot trend lines for top players
        for player in top_players:
            player_data = df[df['Name'] == player].sort_values('Date')
            
            if len(player_data) >= 2:  # Need at least 2 points for a trend
                plt.plot(player_data['Date'], player_data[stat], 
                        marker='o', linewidth=2, label=player, markersize=6)
                lines_plotted = True
        
        # Add legend if we plotted any lines
        if lines_plotted:
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
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
        filename = f"{output_path}/trend_pitching_{stat.lower().replace('/', '_')}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created trend chart for {stat}")
        
    except Exception as e:
        print(f"Error creating trend chart for {stat}: {e}")

if __name__ == "__main__":
    create_pitching_trends()
