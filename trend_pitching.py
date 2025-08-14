import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import glob

# Set style and output directory
sns.set_style("whitegrid")
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

def create_pitching_trends():
    """Create trend charts for pitching stats"""
    try:
        # Get all archived pitching files
        archive_files = glob.glob("archive/pitching_*.csv")
        
        if not archive_files:
            print("No archived pitching data found for trends")
            return
        
        # Stats to track
        trend_stats = ["ERA", "WHIP", "SO", "K/BB", "HR/9", "FIP"]
        
        for stat in trend_stats:
            create_single_trend_chart(archive_files, stat)
        
        print("✓ Pitching trend analysis completed!")
        
    except Exception as e:
        print(f"Error creating pitching trends: {e}")

def create_single_trend_chart(archive_files, stat):
    """Create a trend chart for a single statistic"""
    try:
        # Determine if lower is better for this stat
        lower_is_better = stat in ["ERA", "WHIP", "HR/9", "FIP"]
        title = f"Pitching Trends - {stat}"
        
        plt.figure(figsize=(12, 8))
        
        # Track dates and top players for each date
        date_data = {}
        
        # Process each archive file
        for file in sorted(archive_files):
            try:
                df = pd.read_csv(file)
                if stat not in df.columns:
                    continue
                    
                # Extract date from filename
                date_str = file.split('_')[-1].replace('.csv', '')
                
                # Get top 5 performers for this stat
                if lower_is_better:
                    top_performers = df.nsmallest(5, stat)
                else:
                    top_performers = df.nlargest(5, stat)
                
                # Store data for this date
                date_data[date_str] = top_performers[['Name', stat]].copy()
                
            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue
        
        if not date_data:
            print(f"No data found for {stat}")
            return
        
        # Get all unique players who appeared in top 5
        all_players = set()
        for date_df in date_data.values():
            all_players.update(date_df['Name'].tolist())
        
        # Plot trend lines for each player
        lines_plotted = 0
        for player in list(all_players)[:10]:  # Limit to 10 players max
            dates = []
            values = []
            
            for date_str, date_df in sorted(date_data.items()):
                player_row = date_df[date_df['Name'] == player]
                if not player_row.empty:
                    dates.append(date_str)
                    values.append(player_row[stat].iloc[0])
            
            if len(dates) >= 2:  # Need at least 2 points for a trend
                plt.plot(dates, values, marker='o', linewidth=2, 
                        label=player, markersize=6)
                lines_plotted += 1
        
        # Add legend if we plotted any lines
        if lines_plotted > 0:
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Customize the chart
        plt.title(title, fontsize=14, fontweight='bold')
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
