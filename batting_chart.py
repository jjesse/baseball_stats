import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import batting_stats
from datetime import datetime
import os

# Ensure output directory exists
os.makedirs("docs", exist_ok=True)

# Fetch current season batting stats
df = batting_stats(2025)

# Filter players with at least 100 PA
df = df[df['PA'] >= 100]

# Compute additional stats
df['ISO'] = df['SLG'] - df['AVG']
df['K%'] = df['SO'] / df['PA']
df['BB%'] = df['BB'] / df['PA']

# Select relevant stats
df = df[['Name', 'Team', 'PA', 'AVG', 'HR', 'RBI', 'OBP', 'SLG', 'SB', 'wOBA', 'wRC+', 'BABIP', 'ISO', 'K%', 'BB%']]

# Save CSV backup
df.to_csv("docs/batting_stats.csv", index=False)

# Define chart creation
def create_chart_and_table(df, stat, title, color, ascending=False):
    top = df.sort_values(stat, ascending=ascending).head(10)

    # Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x=stat, y='Name', palette=color)
    plt.title(title)
    plt.tight_layout()
    chart_path = f"docs/batting_{stat.lower().replace('%', 'pct')}_chart.png"
    plt.savefig(chart_path)
    plt.close()

    # Table HTML with dark mode support and interactive features
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="interactive-table.css">
        <style>
            :root {{
                --bg: #ffffff;
                --text: #333333;
                --border: #dddddd;
                --header-bg: #f8f9fa;
                --card-bg: #ffffff;
                --link-shadow: rgba(0, 0, 0, 0.1);
            }}
            
            [data-theme='dark'] {{
                --bg: #1f1f1f;
                --text: #ffffff;
                --border: #555555;
                --header-bg: #2d2d2d;
                --row-even: #2a2a2a;
                --card-bg: #1f1f1f;
                --link-shadow: rgba(255, 255, 255, 0.1);
            }}
            
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 10px;
                background-color: var(--bg);
                color: var(--text);
                overflow: auto;
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
        <script src="interactive-table.js"></script>
        <script>
            // Inherit theme from parent window
            window.onload = function() {{
                try {{
                    const parentTheme = window.parent.document.documentElement.getAttribute('data-theme');
                    if (parentTheme) {{
                        document.documentElement.setAttribute('data-theme', parentTheme);
                    }}
                    
                    // Initialize interactive table
                    const table = document.querySelector('table');
                    if (table) {{
                        table.id = 'batting_{stat.lower().replace('%', 'pct')}_table';
                        table.className = 'stats-table interactive-table';
                        new InteractiveTable(table.id, {{
                            itemsPerPage: 15,
                            searchPlaceholder: "Search {stat} leaders..."
                        }});
                    }}
                }} catch(e) {{
                    console.log('Could not initialize interactive features:', e);
                }}
            }};
        </script>
    </head>
    <body>
        <div class="table-container">
            {top.to_html(index=False, classes='stats-table', escape=False, table_id=f'batting_{stat.lower().replace("%", "pct")}_table')}
        </div>
    </body>
    </html>
    """
    
    table_path = f"docs/batting_{stat.lower().replace('%', 'pct')}_table.html"
    with open(table_path, "w") as f:
        f.write(html_content)

# List of stats to chart
stats_to_plot = [
    ("AVG", "Top 10 Batters by AVG", "Blues"),
    ("HR", "Top 10 Batters by HR", "Reds"),
    ("RBI", "Top 10 Batters by RBI", "Purples"),
    ("OBP", "Top 10 Batters by OBP", "Greens"),
    ("SLG", "Top 10 Batters by SLG", "Oranges"),
    ("SB", "Top 10 Batters by SB", "BuPu"),
    ("wOBA", "Top 10 Batters by wOBA", "YlGn"),
    ("wRC+", "Top 10 Batters by wRC+", "PuRd"),
    ("BABIP", "Top 10 Batters by BABIP", "GnBu"),
    ("ISO", "Top 10 Batters by ISO", "OrRd"),
    ("K%", "Top 10 Batters by K% (Lowest is Best)", "Greys", True),
    ("BB%", "Top 10 Batters by BB%", "PuBu")
]

for entry in stats_to_plot:
    if len(entry) == 4:
        stat, title, color, asc = entry
    else:
        stat, title, color = entry
        asc = False
    create_chart_and_table(df, stat, title, color, asc)

# Write last updated timestamp
with open("docs/last_updated_batting.txt", "w") as f:
    f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
