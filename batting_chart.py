import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import batting_stats
from datetime import datetime
import os

# Ensure output directory exists
output_path = os.environ.get('OUTPUT_PATH', 'docs')
os.makedirs(output_path, exist_ok=True)

# Fetch current season data
df = batting_stats(2025)

# Select relevant stats
df = df[['Name', 'Team', 'AVG', 'HR', 'RBI', 'OBP', 'SLG', 'SB', 'wOBA', 'wRC+', 'BABIP', 'ISO', 'K%', 'BB%']]

# Save CSV backup
df.to_csv(f"{output_path}/batting_stats.csv", index=False)

# Define chart creation function
def create_chart_and_table(df, stat, title, color, ascending=False):
    # For most stats, higher is better, but for K% lower is better
    if stat in ['K%']:
        ascending = not ascending
    top = df.sort_values(stat, ascending=ascending).head(10)

    # Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x=stat, y='Name', hue='Name', palette=color, legend=False)
    plt.title(title)
    plt.tight_layout()
    chart_path = f"{output_path}/{stat.lower().replace('/', '_').replace('%', '_pct')}_chart.png"
    plt.savefig(chart_path)
    plt.close()

    # Table HTML with dark mode support
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
    
    table_path = f"{output_path}/{stat.lower().replace('/', '_').replace('%', '_pct')}_table.html"
    with open(table_path, "w") as f:
        f.write(html_content)

# List of stats to chart
stats_to_plot = [
    ("AVG", "Top 10 Hitters by Batting Average", "Blues"),
    ("HR", "Top 10 Hitters by Home Runs", "Reds"),
    ("RBI", "Top 10 Hitters by RBIs", "Greens"),
    ("OBP", "Top 10 Hitters by On-Base Percentage", "Purples"),
    ("SLG", "Top 10 Hitters by Slugging Percentage", "Oranges"),
    ("SB", "Top 10 Hitters by Stolen Bases", "Greys"),
    ("wOBA", "Top 10 Hitters by wOBA", "BuGn"),
    ("wRC+", "Top 10 Hitters by wRC+", "YlOrRd"),
    ("BABIP", "Top 10 Hitters by BABIP", "viridis"),
    ("ISO", "Top 10 Hitters by ISO", "plasma"),
    ("K%", "Top 10 Hitters by Strikeout Rate (Lower is Better)", "Reds_r"),
    ("BB%", "Top 10 Hitters by Walk Rate", "Blues"),
]

for stat, title, color in stats_to_plot:
    create_chart_and_table(df, stat, title, color)

# Write last updated timestamp
with open(f"{output_path}/last_updated_batting.txt", "w") as f:
    f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        stat, title, color, asc = entry
    else:
        stat, title, color = entry
        asc = False
    create_chart_and_table(df, stat, title, color, asc)

# Write last updated timestamp
with open("docs/last_updated_batting.txt", "w") as f:
    f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
