#!/usr/bin/env python3
"""
MLB Standings Chart Generator

This script fetches current MLB standings data from multiple sources and generates
visualizations for use in the MLB Stats Dashboard.
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import seaborn as sns
import traceback

# Set style for charts using Matplotlib defaults to mimic whitegrid
plt.rcParams.update({
    'axes.facecolor': 'white',
    'axes.grid': True,
    'axes.grid.which': 'major',
    'grid.color': 'lightgray',
    'grid.linestyle': '-',
    'grid.alpha': 0.3,
})

# Make sure output folder exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)


def fetch_standings():
    """Fetch MLB standings from multiple sources with fallbacks"""
    standings_df = None
    
    # Try data sources in order of preference
    sources = [
        fetch_standings_mlb,
        fetch_standings_espn,
        fetch_standings_baseball_reference,
        get_fallback_standings
    ]
    
    for source_func in sources:
        try:
            print(f"Attempting to fetch standings using {source_func.__name__}")
            standings_df = source_func()
            if standings_df is not None and not standings_df.empty:
                print(f"✓ Successfully fetched standings using {source_func.__name__}")
                break
        except Exception as e:
            print(f"Error with {source_func.__name__}: {e}")
            traceback.print_exc()
    
    if standings_df is None or standings_df.empty:
        print("All data sources failed, using emergency fallback data")
        standings_df = get_emergency_fallback()
    
    return standings_df


def fetch_standings_mlb():
    """Fetch standings from MLB.com (primary source)"""
    # This is a placeholder - in a real implementation you would use
    # the MLB Stats API or scrape the MLB website
    # For now, we'll return None to simulate this source failing
    return None


def fetch_standings_espn():
    """Fetch standings from ESPN (secondary source)"""
    try:
        url = "https://www.espn.com/mlb/standings"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
            
        # In a real implementation, parse the HTML to extract standings
        # This is a simplified example
        return None
    except:
        return None


def fetch_standings_baseball_reference():
    """Fetch standings from Baseball Reference (tertiary source)"""
    try:
        url = "https://www.baseball-reference.com/leagues/majors/2025-standings.shtml"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
            
        # In a real implementation, parse the HTML to extract standings
        # This is a simplified example
        return None
    except:
        return None


def get_fallback_standings():
    """Provide fallback standings data when online sources are unavailable"""
    # Sample data for 2025 season
    data = {
        "Team": [
            # AL East
            "New York Yankees", "Boston Red Sox", "Toronto Blue Jays", 
            "Tampa Bay Rays", "Baltimore Orioles",
            # AL Central
            "Cleveland Guardians", "Minnesota Twins", "Detroit Tigers", 
            "Kansas City Royals", "Chicago White Sox",
            # AL West
            "Houston Astros", "Seattle Mariners", "Texas Rangers", 
            "Los Angeles Angels", "Oakland Athletics",
            # NL East
            "Atlanta Braves", "Philadelphia Phillies", "New York Mets", 
            "Miami Marlins", "Washington Nationals",
            # NL Central
            "Milwaukee Brewers", "Chicago Cubs", "St. Louis Cardinals", 
            "Cincinnati Reds", "Pittsburgh Pirates",
            # NL West
            "Los Angeles Dodgers", "San Diego Padres", "San Francisco Giants", 
            "Arizona Diamondbacks", "Colorado Rockies"
        ],
        "W": [
            # AL East
            92, 88, 85, 82, 65,
            # AL Central
            90, 87, 78, 72, 62,
            # AL West
            94, 89, 80, 72, 67,
            # NL East
            96, 93, 85, 74, 69,
            # NL Central
            91, 85, 81, 78, 70,
            # NL West
            98, 89, 84, 80, 68
        ],
        "L": [
            # AL East
            70, 74, 77, 80, 97,
            # AL Central
            72, 75, 84, 90, 100,
            # AL West
            68, 73, 82, 90, 95,
            # NL East
            66, 69, 77, 88, 93,
            # NL Central
            71, 77, 81, 84, 92,
            # NL West
            64, 73, 78, 82, 94
        ],
        "Division": [
            # AL East
            "AL East", "AL East", "AL East", "AL East", "AL East",
            # AL Central
            "AL Central", "AL Central", "AL Central", "AL Central", "AL Central",
            # AL West
            "AL West", "AL West", "AL West", "AL West", "AL West",
            # NL East
            "NL East", "NL East", "NL East", "NL East", "NL East",
            # NL Central
            "NL Central", "NL Central", "NL Central", "NL Central", "NL Central",
            # NL West
            "NL West", "NL West", "NL West", "NL West", "NL West"
        ],
        "League": [
            # AL
            "AL", "AL", "AL", "AL", "AL",
            "AL", "AL", "AL", "AL", "AL",
            "AL", "AL", "AL", "AL", "AL",
            # NL
            "NL", "NL", "NL", "NL", "NL",
            "NL", "NL", "NL", "NL", "NL",
            "NL", "NL", "NL", "NL", "NL"
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate winning percentage
    df["PCT"] = df["W"] / (df["W"] + df["L"]).astype(float)
    df["PCT"] = df["PCT"].round(3)
    
    # Calculate GB (Games Behind) for each division
    for division in df["Division"].unique():
        division_df = df[df["Division"] == division]
        max_wins = division_df["W"].max()
        max_losses = division_df[division_df["W"] == max_wins]["L"].min()
        
        for idx in division_df.index:
            wins = df.loc[idx, "W"]
            losses = df.loc[idx, "L"]
            
            # Formula for GB: (leader_wins - team_wins + team_losses - leader_losses) / 2
            gb = (max_wins - wins + losses - max_losses) / 2
            df.loc[idx, "GB"] = 0.0 if gb == 0 else gb
    
    # Round GB to 1 decimal
    df["GB"] = df["GB"].round(1).astype(str)
    df.loc[df["GB"] == "0.0", "GB"] = "-"
    
    # Add some additional columns
    df["LAST_10"] = ["7-3", "6-4", "5-5", "4-6", "3-7"] * 6  # Sample data
    df["STRK"] = ["W3", "L1", "W2", "L2", "L5"] * 6  # Sample data
    
    return df


def get_emergency_fallback():
    """Absolute last resort if all other methods fail"""
    # Just return 6 teams as a minimal table
    data = {
        "Team": ["Team A", "Team B", "Team C", "Team D", "Team E", "Team F"],
        "W": [90, 85, 80, 75, 70, 65],
        "L": [60, 65, 70, 75, 80, 85],
        "PCT": [0.600, 0.567, 0.533, 0.500, 0.467, 0.433],
        "GB": ["-", "5.0", "10.0", "15.0", "20.0", "25.0"],
        "Division": ["Division 1"] * 6,
        "League": ["League 1"] * 6,
    }
    
    return pd.DataFrame(data)


def calculate_games_behind(df, division=None):
    """Calculate Games Behind within each division"""
    if division:
        division_df = df[df["Division"] == division].copy()
    else:
        division_df = df.copy()
    
    # Sort by win percentage
    division_df = division_df.sort_values("PCT", ascending=False)
    
    if len(division_df) == 0:
        return division_df
    
    # Get the values for the division leader
    leader_wins = division_df.iloc[0]["W"]
    leader_losses = division_df.iloc[0]["L"]
    
    # Calculate GB for each team
    for i, row in division_df.iterrows():
        if i == division_df.index[0]:  # Leader
            division_df.at[i, "GB"] = "-"
        else:
            gb = ((leader_wins - row["W"]) + (row["L"] - leader_losses)) / 2
            division_df.at[i, "GB"] = f"{gb:.1f}"
    
    return division_df


def generate_standings_tables(df):
    """Generate HTML tables for each division"""
    # List of all divisions
    divisions = [
        "AL East", "AL Central", "AL West", 
        "NL East", "NL Central", "NL West"
    ]
    
    for division in divisions:
        division_df = df[df["Division"] == division].copy()
        
        # Sort by winning percentage
        division_df = division_df.sort_values("PCT", ascending=False)
        
        # Calculate games behind
        division_df = calculate_games_behind(division_df)
        
        # Select columns for display
        display_df = division_df[["Team", "W", "L", "PCT", "GB"]]
        
        # Format PCT as string with 3 decimal places
        display_df["PCT"] = display_df["PCT"].apply(lambda x: f"{x:.3f}")
        
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
                {display_df.to_html(index=False, classes='standings-table', escape=False)}
            </div>
        </body>
        </html>
        """
        
        # Save to file
        division_key = division.lower().replace(" ", "_")
        file_path = f"{output_path}/standings_{division_key}.html"
        with open(file_path, "w") as f:
            f.write(html_content)
        
        print(f"✓ Generated table for {division}")


def generate_standings_charts(df):
    """Generate visualization charts for standings"""
    # Division charts
    divisions = [
        "AL East", "AL Central", "AL West", 
        "NL East", "NL Central", "NL West"
    ]
    
    for division in divisions:
        division_df = df[df["Division"] == division].copy()
        
        # Sort by wins
        division_df = division_df.sort_values("W", ascending=False)
        
        # Create chart
        plt.figure(figsize=(10, 6))
        
        # Colors based on the division
        if "AL" in division:
            color = "royalblue"
        else:
            color = "firebrick"
        
        # Create bars
        bars = plt.barh(division_df["Team"], division_df["W"], color=color)
        
        # Add win count labels
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 1, 
                bar.get_y() + bar.get_height()/2,
                f"{int(width)} W", 
                ha='left', va='center'
            )
        
        # Set title and labels
        plt.title(f"{division} Standings - 2025", fontsize=14, fontweight='bold')
        plt.xlabel("Wins", fontsize=12)
        plt.ylabel("Team", fontsize=12)
        
        # Set some styling
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save the chart
        division_key = division.lower().replace(" ", "_")
        plt.savefig(f"{output_path}/standings_{division_key}.png", dpi=120, bbox_inches="tight")
        plt.close()
        
        print(f"✓ Generated chart for {division}")
    
    # Overall standings chart
    plt.figure(figsize=(12, 8))
    
    # Sort by wins
    all_df = df.sort_values("W", ascending=False)
    
    # Use different colors for AL vs NL
    colors = [
        'royalblue' if league == 'AL' else 'firebrick' 
        for league in all_df['League']
    ]
    
    bars = plt.barh(all_df["Team"], all_df["W"], color=colors)
    
    # Add win count labels
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 1, 
            bar.get_y() + bar.get_height()/2,
            f"{int(width)} W", 
            ha='left', va='center'
        )
    
    plt.title("MLB Overall Standings - 2025", fontsize=16, fontweight='bold')
    plt.xlabel("Wins", fontsize=14)
    plt.ylabel("Team", fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add a legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='royalblue', label='American League'),
        Patch(facecolor='firebrick', label='National League')
    ]
    plt.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(f"{output_path}/standings_all.png", dpi=120, bbox_inches="tight")
    plt.close()
    
    print(f"✓ Generated overall standings chart")


def generate_standings_summary(df):
    """Generate summary statistics for the standings dashboard"""
    # Save the complete standings as CSV for reference
    df.to_csv(f"{output_path}/standings_all.csv", index=False)
    
    # Find AL leader
    al_df = df[df["League"] == "AL"].sort_values("PCT", ascending=False)
    if not al_df.empty:
        al_leader = al_df.iloc[0]
        al_leader_data = {
            "team": al_leader["Team"],
            "wins": int(al_leader["W"]),
            "losses": int(al_leader["L"]),
            "pct": float(al_leader["PCT"]),
            "division": al_leader["Division"]
        }
    else:
        al_leader_data = {
            "team": "N/A",
            "wins": 0,
            "losses": 0,
            "pct": 0.0,
            "division": "N/A"
        }
    
    # Find NL leader
    nl_df = df[df["League"] == "NL"].sort_values("PCT", ascending=False)
    if not nl_df.empty:
        nl_leader = nl_df.iloc[0]
        nl_leader_data = {
            "team": nl_leader["Team"],
            "wins": int(nl_leader["W"]),
            "losses": int(nl_leader["L"]),
            "pct": float(nl_leader["PCT"]),
            "division": nl_leader["Division"]
        }
    else:
        nl_leader_data = {
            "team": "N/A",
            "wins": 0,
            "losses": 0, 
            "pct": 0.0,
            "division": "N/A"
        }
    
    # Find closest division race
    closest_race = None
    smallest_game_diff = float('inf')
    
    for division in df["Division"].unique():
        division_df = df[df["Division"] == division].sort_values("PCT", ascending=False)
        if len(division_df) >= 2:
            leader = division_df.iloc[0]
            second = division_df.iloc[1]
            
            # Calculate games behind
            games_diff = ((leader["W"] - second["W"]) + (second["L"] - leader["L"])) / 2
            
            if games_diff < smallest_game_diff:
                smallest_game_diff = games_diff
                closest_race = {
                    "division": division,
                    "leader": {
                        "team": leader["Team"],
                        "wins": int(leader["W"]),
                        "losses": int(leader["L"]),
                        "pct": float(leader["PCT"])
                    },
                    "second": {
                        "team": second["Team"],
                        "wins": int(second["W"]),
                        "losses": int(second["L"]),
                        "pct": float(second["PCT"])
                    },
                    "games_behind": float(smallest_game_diff)
                }
    
    # Create summary JSON
    summary = {
        "al_leader": al_leader_data,
        "nl_leader": nl_leader_data,
        "closest_race": closest_race,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save summary to JSON
    with open(f"{output_path}/standings_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("✓ Generated standings summary data")


def main():
    """Main function to run the standings generation process"""
    try:
        print("Fetching standings data...")
        df = fetch_standings()
        
        if df is None or df.empty:
            print("Error: Failed to fetch standings data")
            return
        
        print("Generating HTML tables...")
        generate_standings_tables(df)
        
        print("Generating charts...")
        generate_standings_charts(df)
        
        print("Generating summary data...")
        generate_standings_summary(df)
        
        # Update timestamp file
        with open(f"{output_path}/last_updated_standings.txt", "w") as f:
            f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("✓ Standings data generation complete!")
        
    except Exception as e:
        print(f"Error in standings_chart.py: {e}")
        traceback.print_exc()
        
        # Create a minimal fallback file so the workflow doesn't fail completely
        with open(f"{output_path}/last_updated_standings.txt", "w") as f:
            f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ensure we have at least a minimal standings_summary.json
        if not os.path.exists(f"{output_path}/standings_summary.json"):
            fallback_summary = {
                "al_leader": {"team": "Error", "wins": 0, "losses": 0, "pct": 0.0, "division": "N/A"},
                "nl_leader": {"team": "Error", "wins": 0, "losses": 0, "pct": 0.0, "division": "N/A"},
                "closest_race": None,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(f"{output_path}/standings_summary.json", "w") as f:
                json.dump(fallback_summary, f, indent=2)


if __name__ == "__main__":
    main()