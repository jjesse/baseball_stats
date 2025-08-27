#!/usr/bin/env python3
"""
Batting trend analyzer - Tracks batting trends over time for top players
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import glob
from utils import save_html_table, save_standings_chart, log_error

# Set style and output directory
sns.set_style("whitegrid")
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

def create_batting_trends():
    """Create trend charts for batting stats"""
    try:
        # Get all archived batting files
        archive_files = glob.glob("archive/batting_*.csv")
        
        if not archive_files:
            print("No archived batting data found for trends")
            return
        
        # Stats to track
        trend_stats = ["AVG", "HR", "RBI", "OBP", "SLG", "wOBA"]
        
        for stat in trend_stats:
            plt.figure(figsize=(12, 8))
            lines_plotted = 0
            
            # Process each archive file
            for file in sorted(archive_files):
                try:
                    df = pd.read_csv(file)
                    if stat in df.columns:
                        # Get top 5 performers for this stat
                        top_performers = df.nlargest(5, stat)
                        
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
            
            plt.title(f"Batting Trends - {stat}")
            plt.xlabel("Date")
            plt.ylabel(stat)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart
            chart_path = f"{output_path}/trend_batting_{stat.lower()}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Created trend chart for {stat}")
        
        print("✓ Batting trend analysis completed!")
        
    except Exception as e:
        print(f"Error creating batting trends: {e}")

if __name__ == "__main__":
    create_batting_trends()
