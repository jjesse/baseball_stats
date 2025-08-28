import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Utility: Standardized error logging
def log_error(context, e):
    print(f"Error in {context}: {e}")

# Utility: HTML table with dark mode support
def save_html_table(df, filename, title=None, output_path="docs"):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title if title else 'MLB Standings'}</title>
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
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 10px; background-color: var(--bg); color: var(--text); overflow: hidden; }}
            .table-container {{ width: 100%; max-width: 100%; overflow-x: auto; }}
            table {{ width: 100%; border-collapse: collapse; background-color: var(--bg); margin: 0 auto; }}
            th, td {{ border: 1px solid var(--border); padding: 8px; text-align: center; color: var(--text) !important; }}
            th {{ background-color: var(--header-bg) !important; font-weight: bold; color: var(--text) !important; }}
            tr:nth-child(even) td {{ background-color: var(--row-even, #f9f9f9) !important; color: var(--text) !important; }}
            tr:nth-child(odd) td {{ background-color: var(--bg) !important; color: var(--text) !important; }}
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
        <div class="table-container">
            {df.to_html(index=False, classes='standings-table', escape=False)}
        </div>
    </body>
    </html>
    """
    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, filename), "w") as f:
        f.write(html_content)

# Utility: Standings chart creation
def save_standings_chart(df, title, filename, team_col="Team", output_path="docs"):
    try:
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(data=df, x=team_col, y="W")
        plt.title(title)
        plt.xlabel("Team")
        plt.ylabel("Wins")
        plt.xticks(rotation=45)
        for i, p in enumerate(ax.patches):
            ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2.0, p.get_height()), ha="center", va="bottom")
        plt.tight_layout()
        os.makedirs(output_path, exist_ok=True)
        plt.savefig(os.path.join(output_path, filename), dpi=100)
        plt.close()
    except Exception as e:
        log_error("save_standings_chart", e)
