import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

def create_pitching_trends():
    """Create trend charts for pitching statistics"""
    try:
        # Look for archived pitching data
        archive_files = sorted(glob.glob("archive/pitching_*.csv"))
        
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
            print("No valid historical pitching data found")
            return
        
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        
        # Stats to track trends for
        trend_stats = ['ERA', 'WHIP', 'SO', 'K/BB', 'FIP', 'HR/9']
        
        for stat in trend_stats:
            if stat not in combined_df.columns:
                continue
                
            try:
                # Get top 5 players by latest performance
                latest_date = combined_df['Date'].max()
                latest_data = combined_df[combined_df['Date'] == latest_date]
                
                if stat in ['ERA', 'WHIP', 'HR/9']:  # Lower is better
                    top_players = latest_data.nsmallest(5, stat)['Name'].tolist()
                else:  # Higher is better
                    top_players = latest_data.nlargest(5, stat)['Name'].tolist()
                
                # Create trend chart
                plt.figure(figsize=(12, 8))
                
                for player in top_players:
                    player_data = combined_df[combined_df['Name'] == player].sort_values('Date')
                    if len(player_data) >= 2:
                        plt.plot(player_data['Date'], player_data[stat], marker='o', label=player, linewidth=2)
                
                plt.title(f'Pitching Trends - {stat}', fontsize=16, fontweight='bold')
                plt.xlabel('Date', fontsize=12)
                plt.ylabel(stat, fontsize=12)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Save chart
                chart_path = f"{output_path}/trend_pitching_{stat.lower().replace('/', '_')}.png"
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"✓ Created trend chart for {stat}")
                
            except Exception as e:
                print(f"Error creating trend chart for {stat}: {e}")
        
        print("✓ Pitching trend analysis completed")
        
    except Exception as e:
        print(f"Error in pitching trend analysis: {e}")

if __name__ == "__main__":
    create_pitching_trends()
            if lines_plotted:
                plt.title(f"{stat} Trends Over Time", fontsize=14, fontweight="bold")
                plt.xlabel("Date", fontsize=12)
                plt.ylabel(stat, fontsize=12)
                plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                filename = f"{output_path}/trend_{stat.lower().replace('/', '_')}.png"
                plt.savefig(filename, dpi=150, bbox_inches="tight")
                print(f"Generated pitching trend chart for {stat}")
            else:
                print(f"No valid trend lines for {stat}, skipping chart generation")

            plt.close()
        except Exception as e:
            print(f"Error creating trend chart for {stat}: {e}")
            continue

    print("✓ Pitching trend analysis completed successfully!")

except Exception as e:
    print(f"Critical error in trend_pitching.py: {e}")
    # Ensure we don't leave the workflow hanging
    raise
