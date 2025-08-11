#!/usr/bin/env python3
"""
Simple defensive stats generator that works without external dependencies
"""
import os
import json
from datetime import datetime

# Make sure output folder exists
output_path = os.environ.get("OUTPUT_PATH", "../../docs")
os.makedirs(output_path, exist_ok=True)

def create_simple_defensive_data():
    """Create basic defensive data and HTML files"""
    
    # Sample defensive leaders data
    defensive_leaders = {
        "fld_pct": [
            {"Name": "Matt Olson", "Team": "ATL", "Pos": "1B", "Fld%": 0.998},
            {"Name": "Will Smith", "Team": "LAD", "Pos": "C", "Fld%": 0.997},
            {"Name": "Freddie Freeman", "Team": "LAD", "Pos": "1B", "Fld%": 0.997},
            {"Name": "Salvador Perez", "Team": "KC", "Pos": "C", "Fld%": 0.996},
            {"Name": "Vladimir Guerrero Jr.", "Team": "TOR", "Pos": "1B", "Fld%": 0.996},
        ],
        "po": [
            {"Name": "Matt Olson", "Team": "ATL", "Pos": "1B", "PO": 852},
            {"Name": "Freddie Freeman", "Team": "LAD", "Pos": "1B", "PO": 845},
            {"Name": "Vladimir Guerrero Jr.", "Team": "TOR", "Pos": "1B", "PO": 825},
            {"Name": "Salvador Perez", "Team": "KC", "Pos": "C", "PO": 625},
            {"Name": "J.T. Realmuto", "Team": "PHI", "Pos": "C", "PO": 580},
        ],
        "a": [
            {"Name": "Francisco Lindor", "Team": "NYM", "Pos": "SS", "A": 325},
            {"Name": "Trea Turner", "Team": "PHI", "Pos": "SS", "A": 312},
            {"Name": "Bo Bichette", "Team": "TOR", "Pos": "SS", "A": 298},
            {"Name": "Jose Altuve", "Team": "HOU", "Pos": "2B", "A": 285},
            {"Name": "Gleyber Torres", "Team": "NYY", "Pos": "2B", "A": 275},
        ],
        "dp": [
            {"Name": "Matt Olson", "Team": "ATL", "Pos": "1B", "DP": 95},
            {"Name": "Freddie Freeman", "Team": "LAD", "Pos": "1B", "DP": 88},
            {"Name": "Vladimir Guerrero Jr.", "Team": "TOR", "Pos": "1B", "DP": 82},
            {"Name": "Francisco Lindor", "Team": "NYM", "Pos": "SS", "DP": 78},
            {"Name": "Trea Turner", "Team": "PHI", "Pos": "SS", "DP": 72},
        ],
        "e": [
            {"Name": "Will Smith", "Team": "LAD", "Pos": "C", "E": 2},
            {"Name": "Matt Olson", "Team": "ATL", "Pos": "1B", "E": 2},
            {"Name": "Kyle Tucker", "Team": "HOU", "Pos": "RF", "E": 2},
            {"Name": "Salvador Perez", "Team": "KC", "Pos": "C", "E": 3},
            {"Name": "Freddie Freeman", "Team": "LAD", "Pos": "1B", "E": 3},
        ],
        "cs_pct": [
            {"Name": "Salvador Perez", "Team": "KC", "Pos": "C", "CS%": 0.324},
            {"Name": "J.T. Realmuto", "Team": "PHI", "Pos": "C", "CS%": 0.298},
            {"Name": "Will Smith", "Team": "LAD", "Pos": "C", "CS%": 0.285},
            {"Name": "Tyler Stephenson", "Team": "CIN", "Pos": "C", "CS%": 0.267},
            {"Name": "William Contreras", "Team": "MIL", "Pos": "C", "CS%": 0.245},
        ]
    }
    
    # Create HTML tables for each stat
    stats_info = {
        "fld_pct": ("Fielding Percentage Leaders", "Fld%"),
        "po": ("Putout Leaders", "PO"),
        "a": ("Assist Leaders", "A"),
        "dp": ("Double Play Leaders", "DP"),
        "e": ("Fewest Errors", "E"),
        "cs_pct": ("Caught Stealing % Leaders", "CS%")
    }
    
    for stat_key, (title, stat_col) in stats_info.items():
        create_html_table(defensive_leaders[stat_key], stat_key, title, stat_col)
        create_placeholder_chart(stat_key, title)
    
    # Create a simple CSV file
    create_defensive_csv()
    
    # Create update timestamp
    with open(f"{output_path}/last_updated_defense.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("✓ Created basic defensive statistics files")

def create_html_table(data, stat_key, title, stat_col):
    """Create a simple HTML table"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
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
            
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                background-color: var(--bg);
                margin: 0 auto;
                font-size: 14px;
            }}
            
            th, td {{ 
                border: 1px solid var(--border); 
                padding: 8px; 
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
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Team</th>
                    <th>Pos</th>
                    <th>{stat_col}</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for player in data:
        html_content += f"""
                <tr>
                    <td>{player['Name']}</td>
                    <td>{player['Team']}</td>
                    <td>{player['Pos']}</td>
                    <td>{player.get(stat_col, 'N/A')}</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    filename = f"defense_{stat_key}_table.html"
    with open(f"{output_path}/{filename}", "w") as f:
        f.write(html_content)
    
    print(f"✓ Created {filename}")

def create_placeholder_chart(stat_key, title):
    """Create placeholder chart files"""
    
    # Create a simple SVG placeholder
    svg_content = f'''
    <svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#f8f9fa"/>
        <text x="50%" y="50%" text-anchor="middle" font-family="Arial" font-size="24" fill="#333">
            {title}
        </text>
        <text x="50%" y="60%" text-anchor="middle" font-family="Arial" font-size="16" fill="#666">
            Chart will be generated when pybaseball is available
        </text>
    </svg>
    '''
    
    filename = f"defense_{stat_key}_chart.png"
    # For now, create a simple text file indicating the chart placeholder
    with open(f"{output_path}/{filename.replace('.png', '_placeholder.svg')}", "w") as f:
        f.write(svg_content)
    
    print(f"✓ Created placeholder for {filename}")

def create_defensive_csv():
    """Create a simple defensive stats CSV"""
    
    csv_content = """Name,Team,Pos,G,Inn,PO,A,E,DP,Fld%,CS%
Matt Olson,ATL,1B,98,850.0,852,68,2,95,0.998,0.000
Will Smith,LAD,C,92,800.0,555,45,2,5,0.997,0.285
Freddie Freeman,LAD,1B,95,825.0,825,72,3,88,0.997,0.000
Salvador Perez,KC,C,98,850.0,625,48,3,8,0.996,0.324
Vladimir Guerrero Jr.,TOR,1B,96,840.0,845,65,4,82,0.996,0.000
Francisco Lindor,NYM,SS,98,850.0,145,325,8,78,0.983,0.000
J.T. Realmuto,PHI,C,95,820.0,580,52,4,6,0.994,0.298
Jose Altuve,HOU,2B,98,850.0,185,285,5,68,0.989,0.000
Trea Turner,PHI,SS,95,825.0,138,312,9,72,0.980,0.000
Nolan Arenado,STL,3B,98,850.0,85,245,6,28,0.982,0.000"""
    
    with open(f"{output_path}/defensive_stats.csv", "w") as f:
        f.write(csv_content)
    
    print("✓ Created defensive_stats.csv")

if __name__ == "__main__":
    print("Generating basic defensive statistics...")
    create_simple_defensive_data()
    print("✓ Basic defensive statistics generation completed!")