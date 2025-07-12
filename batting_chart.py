import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import batting_stats
from datetime import datetime
import os

# Ensure output directory exists
output_path = os.environ.get('OUTPUT_PATH', 'docs')
os.makedirs(output_path, exist_ok=True)

try:
    # Fetch current season batting data
    df = batting_stats(2025)
    
    # Select relevant batting stats
    df = df[['Name', 'Team', 'G', 'AB', 'R', 'H', 'HR', 'RBI', 'SB', 'BB', 'SO', 'AVG', 'OBP', 'SLG', 'OPS', 'wOBA', 'wRC+', 'BABIP', 'ISO', 'K%', 'BB%']]
    
    # Filter out players with minimal playing time
    df = df[df['AB'] >= 50]  # At least 50 at-bats
    
    # Save CSV for archiving
    df.to_csv(f"{output_path}/batting_stats.csv", index=False)
    
    def create_chart_and_table(df, stat, title, color, ascending):
        """Create chart and HTML table for a given stat"""
        try:
            top = df.sort_values(stat, ascending=ascending).head(10)
            
            # Create chart
            plt.figure(figsize=(12, 8))
            sns.barplot(data=top, x=stat, y='Name', hue='Name', palette=color, legend=False)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel(stat, fontsize=12)
            plt.ylabel('Player', fontsize=12)
            plt.tight_layout()
            
            chart_path = f"{output_path}/batting_{stat.lower().replace('%', '_pct').replace('/', '_')}_chart.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Create HTML table with dark mode support
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    :root {{
                        --bg: #ffffff;
                        --text: #333333;
                        --border: #dddddd;
                        --header-bg: #f8f9fa;
                    }}
                    
                    [data-theme='dark'] {{
                        --bg: #1f1f1f;
                        --text: #ffffff;
                        --border: #555555;
                        --header-bg: #2d2d2d;
                        --row-even: #2a2a2a;
                    }}
                    
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 10px;
                        background-color: var(--bg);
                        color: var(--text);
                        overflow: hidden;
                    }}
                    
                    .table-container {{
                        width: 100%;
                        max-width: 100%;
                        overflow-x: auto;
                    }}
                    
                    table {{ 
                        width: 100%; 
                        border-collapse: collapse; 
                        background-color: var(--bg);
                        margin: 0 auto;
                        font-size: 14px;
                    }}
                    
                    th, td {{ 
                        border: 1px solid var(--border); 
                        padding: 6px; 
                        text-align: center;
                        color: var(--text) !important;
                    }}
                    
                    th {{ 
                        background-color: var(--header-bg) !important;
                        font-weight: bold;
                        color: var(--text) !important;
                    }}
                    
                    tr:nth-child(even) td {{ 
                        background-color: var(--row-even, #f9f9f9) !important;
                        color: var(--text) !important;
                    }}
                    
                    tr:nth-child(odd) td {{ 
                        background-color: var(--bg) !important;
                        color: var(--text) !important;
                    }}
                </style>
                <script>
                    // Inherit theme from parent window
                    window.onload = function() {{
                        try {{
                            const parentTheme = window.parent.document.documentElement.getAttribute('data-theme');
                            if (parentTheme) {{
                                document.documentElement.setAttribute('data-theme', parentTheme);
                            }}
                        }} catch(e) {{
                            // Cross-origin issues, use default
                        }}
                    }};
                </script>
            </head>
            <body>
                <div class="table-container">
                    {top.to_html(index=False, classes='stats-table', escape=False)}
                </div>
            </body>
            </html>
            """
            
            table_path = f"{output_path}/batting_{stat.lower().replace('%', '_pct').replace('/', '_')}_table.html"
            with open(table_path, "w") as f:
                f.write(html_content)
                
            print(f"✓ Created chart and table for {stat}")
            
        except Exception as e:
            print(f"Error creating chart for {stat}: {e}")
    
    # List of batting stats to chart
    stats_to_plot = [
        ("AVG", "Top 10 Hitters by Batting Average", "Blues", False),
        ("HR", "Top 10 Hitters by Home Runs", "Reds", False),
        ("RBI", "Top 10 Hitters by RBIs", "Greens", False),
        ("OBP", "Top 10 Hitters by On-Base Percentage", "Purples", False),
        ("SLG", "Top 10 Hitters by Slugging Percentage", "Oranges", False),
        ("SB", "Top 10 Hitters by Stolen Bases", "BuGn", False),
        ("wOBA", "Top 10 Hitters by wOBA", "viridis", False),
        ("wRC+", "Top 10 Hitters by wRC+", "plasma", False),
        ("BABIP", "Top 10 Hitters by BABIP", "coolwarm", False),
        ("ISO", "Top 10 Hitters by Isolated Power", "YlOrRd", False),
        ("K%", "Lowest K% (Best Contact)", "Greys", True),
        ("BB%", "Top 10 Hitters by Walk Rate", "BuPu", False)
    ]
    
    # Generate charts and tables for each stat
    for stat, title, color, asc in stats_to_plot:
        if stat in df.columns:
            create_chart_and_table(df, stat, title, color, asc)
        else:
            print(f"Warning: {stat} not found in data columns")
    
    # Write last updated timestamp
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("✓ Batting charts and tables generated successfully!")

except Exception as e:
    print(f"Error in batting_chart.py: {e}")
    # Create a minimal fallback file so the workflow doesn't fail completely
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raise
    if 'BB%' in df.columns:
        stats_to_plot.append(("BB%", "Top 10 Hitters by Walk Rate", "BuPu", False))
    
    # Generate charts and tables for each stat
    for stat, title, color, asc in stats_to_plot:
        create_chart_and_table(df, stat, title, color, asc)
    
    # Write last updated timestamp
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("✓ Batting charts and tables generated successfully!")

except Exception as e:
    print(f"Error in batting_chart.py: {e}")
    # Create a minimal fallback file so the workflow doesn't fail completely
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raise
    raise
