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
    print("Fetching batting stats for 2025 season...")
    df = batting_stats(2025)

    # Select relevant stats
    df = df[["Name", "Team", "AVG", "HR", "RBI", "OBP", "SLG", "SB", "wOBA", "wRC+", "BABIP", "ISO", "K%", "BB%"]]

    # Save CSV backup
    df.to_csv(f"{output_path}/batting_stats.csv", index=False)
    print("✓ Saved batting stats CSV backup")

    # Create charts and tables for each stat
    stats_to_plot = [
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
        ("K%", "Lowest K% (Best Contact)", "hot"),
        ("BB%", "Top 10 Batters by Walk Rate", "winter")
    ]
    
    for stat, title, color in stats_to_plot:
        print(f"Processing {stat}...")
        # Sort in ascending order only for K%
        ascending = stat == "K%"
        top = df.sort_values(stat, ascending=ascending).head(10)
        
        # Create chart
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top, x=stat, y="Name", palette=color)
        plt.title(title)
        plt.tight_layout()
        
        # Save chart - use batting_ prefix to avoid naming conflicts
        safe_stat = stat.lower().replace("%", "_pct").replace("+", "_plus")
        chart_path = f"{output_path}/batting_{safe_stat}_chart.png"
        plt.savefig(chart_path)
        plt.close()
        
        # Create simple HTML table with dark mode support
        html = f"""<!DOCTYPE html>
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
}}

table {{ 
    width: 100%; 
    border-collapse: collapse; 
    margin: 0 auto;
    font-size: 14px;
}}

th, td {{ 
    border: 1px solid var(--border); 
    padding: 6px; 
    text-align: center;
}}

th {{ 
    background-color: var(--header-bg);
    font-weight: bold;
}}

tr:nth-child(even) td {{ 
    background-color: var(--row-even, #f9f9f9);
}}
</style>
<script>
window.onload = function() {{
    try {{
        const parentTheme = window.parent.document.documentElement.getAttribute('data-theme');
        if (parentTheme) {{
            document.documentElement.setAttribute('data-theme', parentTheme);
        }}
    }} catch(e) {{}}
}};
</script>
</head>
<body>
{top.to_html(index=False)}
</body>
</html>"""
        
        # Save HTML table with batting_ prefix
        table_path = f"{output_path}/batting_{safe_stat}_table.html"
        with open(table_path, "w") as f:
            f.write(html)
        
        print(f"✓ Created {stat} chart and table")
    
    # Write last updated timestamp
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("✓ Batting charts and tables generated successfully!")

except Exception as e:
    print(f"Error in batting_chart.py: {e}")
    # Create a minimal fallback file
    with open(f"{output_path}/last_updated_batting.txt", "w") as f:
        f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
