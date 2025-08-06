import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import batting_stats
from datetime import datetime
import os

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

try:
    # Fetch current season data
    df = batting_stats(2025)

    # Select relevant stats
    df = df[["Name", "Team", "AVG", "HR", "RBI", "OBP", "SLG", "SB", "wOBA", "wRC+", "BABIP", "ISO", "K%", "BB%"]]

    # Save CSV backup
    df.to_csv(f"{output_path}/batting_stats.csv", index=False)

    def create_chart_and_table(df, stat, title, color):
        try:
            # For K%, we want the lowest values (best contact hitters)
            ascending = stat == "K%"
            top = df.sort_values(stat, ascending=ascending).head(10)

            # Create chart
            plt.figure(figsize=(10, 6))
            sns.barplot(data=top, x=stat, y="Name", hue="Name", palette=color, legend=False)
            plt.title(title)
            plt.tight_layout()
            chart_path = f"{output_path}/batting_{stat.lower().replace('%', '_pct')}_chart.png"
            plt.savefig(chart_path)
            plt.close()

            # Create simple HTML table with dark mode support
            html = """<!DOCTYPE html>
<html>
<head>
    <style>
        :root {
            --bg: #ffffff;
            --text: #333333;
            --border: #dddddd;
            --header-bg: #f8f9fa;
        }
        
        [data-theme='dark'] {
            --bg: #1f1f1f;
            --text: #ffffff;
            --border: #555555;
            --header-bg: #2d2d2d;
            --row-even: #2a2a2a;
        }
        
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 10px;
            background-color: var(--bg);
            color: var(--text);
        }
        
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background-color: var(--bg);
            margin: 0 auto;
            font-size: 14px;
        }
        
        th, td { 
            border: 1px solid var(--border); 
            padding: 6px; 
            text-align: center;
            color: var(--text) !important;
        }
        
        th { 
            background-color: var(--header-bg) !important;
            font-weight: bold;
        }
        
        tr:nth-child(even) td { 
            background-color: var(--row-even, #f9f9f9) !important;
        }
    </style>
    <script>
        window.onload = function() {
            try {
                const parentTheme = window.parent.document.documentElement.getAttribute('data-theme');
                if (parentTheme) {
                    document.documentElement.setAttribute('data-theme', parentTheme);
                }
            } catch(e) {
                // Cross-origin issues, use default
            }
        };
    </script>
</head>
<body>
"""
            html += top.to_html(index=False)
            html += """
</body>
</html>"""

            table_path = f"{output_path}/batting_{stat.lower().replace('%', '_pct')}_table.html"
            with open(table_path, "w") as f:
                f.write(html)

            print(f"✓ Created chart and table for {stat}")
            
        except Exception as e:
            print(f"Error creating chart for {stat}: {e}")

    # Stats to plot
    stats = [
        ("AVG", "Top 10 Batters by Average", "Blues"),
        ("HR", "Top 10 Batters by Home Runs", "Reds"),
        ("RBI", "Top 10 Batters by RBI", "Greens"),
        ("OBP", "Top 10 Batters by On-Base Percentage", "Purples"),
        ("SLG", "Top 10 Batters by Slugging", "Oranges"),
        ("SB", "Top 10 Batters by Stolen Bases", "BuGn"),
        ("wOBA", "Top 10 Batters by wOBA", "viridis"),
        ("wRC+", "Top 10 Batters by wRC+", "plasma"),
        ("BABIP", "Top 10 Batters by BABIP", "magma"),
        ("ISO", "Top 10 Batters by ISO", "cool"),
        ("K%", "Best Contact Hitters (Lowest K%)", "hot"),
        ("BB%", "Top 10 Batters by Walk Rate", "winter")
    ]

    for stat, title, color in stats:
        create_chart_and_table(df, stat, title, color)

    # Write timestamp
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("✓ Batting charts and tables generated successfully!")

except Exception as e:
    print(f"Error in batting_chart.py: {e}")
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raise
except Exception as e:
    print(f"Error in batting_chart.py: {e}")
    # Create a minimal fallback file so the workflow doesn't fail completely
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raise
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raise
        create_chart_and_table(df, stat, title, color)

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
    print(f"Error in batting_chart.py: {e}")
    # Create a minimal fallback file so the workflow doesn't fail completely
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raise
        ("BABIP", "Top 10 Hitters by BABIP", "coolwarm", False),
        ("ISO", "Top 10 Hitters by Isolated Power", "YlOrRd", False),
        ("K%", "Lowest K% (Best Contact)", "Greys", True),
        ("BB%", "Top 10 Hitters by Walk Rate", "BuPu", False),
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
