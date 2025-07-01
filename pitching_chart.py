import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import pitching_stats
from datetime import datetime
import os

# Ensure output directory exists
os.makedirs("docs", exist_ok=True)

# Fetch current season data
df = pitching_stats(2025)

# Select relevant stats
df = df[['Name', 'Team', 'W', 'L', 'ERA', 'SO', 'BB', 'WHIP', 'K/BB', 'HR/9', 'FIP']]

# Save CSV backup (optional)
df.to_csv("docs/season_stats.csv", index=False)

# Define chart creation

def create_chart_and_table(df, stat, title, color):
    top = df.sort_values(stat, ascending=(stat in ['BB', 'ERA', 'WHIP', 'HR/9'])).head(10)

    # Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x=stat, y='Name', palette=color)
    plt.title(title)
    plt.tight_layout()
    chart_path = f"docs/{stat.lower().replace('/', '_')}_chart.png"
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
                        table.id = 'pitching_{stat.lower().replace("/", "_")}_table';
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
            {top.to_html(index=False, classes='stats-table', escape=False, table_id=f'pitching_{stat.lower().replace("/", "_")}_table')}
        </div>
    </body>
    </html>
    """
    
    table_path = f"docs/{stat.lower().replace('/', '_')}_table.html"
    with open(table_path, "w") as f:
        f.write(html_content)


# List of stats to chart
stats_to_plot = [
    ("WHIP", "Top 10 Pitchers by WHIP", "Blues"),
    ("ERA", "Top 10 Pitchers by ERA", "Greens"),
    ("SO", "Top 10 Pitchers by Strikeouts", "Purples"),
    ("BB", "Top 10 Pitchers by Walks", "Oranges"),
    ("K/BB", "Top 10 Pitchers by K/BB Ratio", "Reds"),
    ("HR/9", "Top 10 Pitchers by HR/9", "Greys"),
    ("FIP", "Top 10 Pitchers by FIP", "BuGn"),
]

for stat, title, color in stats_to_plot:
    create_chart_and_table(df, stat, title, color)

# Write last updated timestamp with proper format
with open("docs/last_updated_pitching.txt", "w") as f:
    f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
