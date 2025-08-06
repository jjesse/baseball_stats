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
            plt.figure(figsize=(12, 8))
            lines_plotted = 0
            
            # Process each archive file
            for file in sorted(archive_files):
                try:
                    df = pd.read_csv(file)
                    if stat in df.columns:
                        # Get top 5 performers for this stat
                        ascending = stat in ["ERA", "WHIP", "HR/9", "FIP"]
                        top_performers = df.nlargest(5, stat) if not ascending else df.nsmallest(5, stat)
                        
                        # Extract date from filename
                        date_str = file.split('_')[-1].replace('.csv', '')
                        
                        for _, player in top_performers.iterrows():
                            plt.plot([date_str], [player[stat]], 'o-', label=f"{player['Name']}")
                            lines_plotted += 1
                
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    continue
            
            # Add legend if we plotted any lines
            if lines_plotted:
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.title(f"Pitching Trends - {stat}")
            plt.xlabel("Date")
            plt.ylabel(stat)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart
            chart_path = f"{output_path}/trend_pitching_{stat.lower().replace('/', '_')}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Created trend chart for {stat}")
        
        print("✓ Pitching trend analysis completed!")
        
    except Exception as e:
        print(f"Error creating pitching trends: {e}")

if __name__ == "__main__":
    create_pitching_trends()
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
