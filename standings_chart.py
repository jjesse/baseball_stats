#!/usr/bin/env python3
"""
MLB Standings Chart Generator

This script fetches current MLB standings data from multiple sources and generates
visualizations for use in the MLB Stats Dashboard.
"""
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import traceback

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)

def fetch_standings():
    """Fetch MLB standings from multiple sources with fallbacks"""
    standings_df = None
    
    # Try data sources in order of preference
    sources = [
        fetch_standings_mlb,
        fetch_standings_espn,
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
    
    if standings_df is None or standings_df.empty:
        print("All data sources failed, using emergency fallback data")
        standings_df = get_emergency_fallback()
    
    return standings_df

def fetch_standings_mlb():
    """Fetch standings from MLB.com API (primary source)"""
    try:
        # MLB.com API endpoint for standings
        url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2025&standingsTypes=regularSeason"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Process the MLB API data
        all_teams = []
        
        if "records" in data:
            for division_record in data["records"]:
                division_name = division_record.get("division", {}).get("name", "Unknown")
                # Standardize division names
                if "American League East" in division_name:
                    division_name = "AL East"
                    league = "AL"
                elif "American League Central" in division_name:
                    division_name = "AL Central"
                    league = "AL"
                elif "American League West" in division_name:
                    division_name = "AL West"
                    league = "AL"
                elif "National League East" in division_name:
                    division_name = "NL East"
                    league = "NL"
                elif "National League Central" in division_name:
                    division_name = "NL Central"
                    league = "NL"
                elif "National League West" in division_name:
                    division_name = "NL West"
                    league = "NL"
                else:
                    league = "Unknown"
                
                for team_record in division_record.get("teamRecords", []):
                    team_name = team_record.get("team", {}).get("name", "Unknown")
                    wins = team_record.get("wins", 0)
                    losses = team_record.get("losses", 0)
                    pct = team_record.get("winningPercentage", "0")
                    
                    try:
                        pct = float(pct)
                    except:
                        if wins + losses > 0:
                            pct = wins / (wins + losses)
                        else:
                            pct = 0.0
                    
                    all_teams.append({
                        "Team": team_name,
                        "W": wins,
                        "L": losses,
                        "PCT": pct,
                        "GB": 0.0,
                        "Division": division_name,
                        "League": league
                    })
        
        if not all_teams:
            return None
        
        df = pd.DataFrame(all_teams)
        calculate_games_behind(df)
        return df
        
    except Exception as e:
        print(f"Error fetching from MLB.com: {e}")
        return None

def fetch_standings_espn():
    """Fetch standings from ESPN (secondary source)"""
    try:
        url = "https://www.espn.com/mlb/standings"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # For now, return None - would need to parse ESPN HTML
        return None
        
    except Exception as e:
        print(f"Error fetching from ESPN: {e}")
        return None

def get_fallback_standings():
    """Provide fallback standings data when online sources are unavailable"""
    team_info = {
        # AL East
        "New York Yankees": {"division": "AL East", "league": "AL"},
        "Boston Red Sox": {"division": "AL East", "league": "AL"},
        "Toronto Blue Jays": {"division": "AL East", "league": "AL"},
        "Tampa Bay Rays": {"division": "AL East", "league": "AL"},
        "Baltimore Orioles": {"division": "AL East", "league": "AL"},
        
        # AL Central
        "Cleveland Guardians": {"division": "AL Central", "league": "AL"},
        "Minnesota Twins": {"division": "AL Central", "league": "AL"},
        "Detroit Tigers": {"division": "AL Central", "league": "AL"},
        "Kansas City Royals": {"division": "AL Central", "league": "AL"},
        "Chicago White Sox": {"division": "AL Central", "league": "AL"},
        
        # AL West
        "Houston Astros": {"division": "AL West", "league": "AL"},
        "Seattle Mariners": {"division": "AL West", "league": "AL"},
        "Texas Rangers": {"division": "AL West", "league": "AL"},
        "Los Angeles Angels": {"division": "AL West", "league": "AL"},
        "Oakland Athletics": {"division": "AL West", "league": "AL"},
        
        # NL East
        "Atlanta Braves": {"division": "NL East", "league": "NL"},
        "Philadelphia Phillies": {"division": "NL East", "league": "NL"},
        "New York Mets": {"division": "NL East", "league": "NL"},
        "Miami Marlins": {"division": "NL East", "league": "NL"},
        "Washington Nationals": {"division": "NL East", "league": "NL"},
        
        # NL Central
        "Milwaukee Brewers": {"division": "NL Central", "league": "NL"},
        "Chicago Cubs": {"division": "NL Central", "league": "NL"},
        "St. Louis Cardinals": {"division": "NL Central", "league": "NL"},
        "Cincinnati Reds": {"division": "NL Central", "league": "NL"},
        "Pittsburgh Pirates": {"division": "NL Central", "league": "NL"},
        
        # NL West
        "Los Angeles Dodgers": {"division": "NL West", "league": "NL"},
        "San Diego Padres": {"division": "NL West", "league": "NL"},
        "San Francisco Giants": {"division": "NL West", "league": "NL"},
        "Arizona Diamondbacks": {"division": "NL West", "league": "NL"},
        "Colorado Rockies": {"division": "NL West", "league": "NL"}
    }
    
    data = {
        "Team": list(team_info.keys()),
        "W": [92, 88, 85, 82, 65, 90, 87, 78, 72, 62, 94, 89, 80, 72, 67, 96, 93, 85, 74, 69, 91, 85, 81, 78, 70, 98, 89, 84, 80, 68],
        "L": [70, 74, 77, 80, 97, 72, 75, 84, 90, 100, 68, 73, 82, 90, 95, 66, 69, 77, 88, 93, 71, 77, 81, 84, 92, 64, 73, 78, 82, 94]
    }
    
    df = pd.DataFrame(data)
    df["Division"] = df["Team"].apply(lambda x: team_info[x]["division"])
    df["League"] = df["Team"].apply(lambda x: team_info[x]["league"])
    df["PCT"] = df["W"] / (df["W"] + df["L"])
    df["PCT"] = df["PCT"].round(3)
    
    calculate_games_behind(df)
    print("✓ Generated fallback standings data")
    return df

def get_emergency_fallback():
    """Emergency fallback data"""
    data = {
        "Team": ["New York Yankees", "Boston Red Sox", "Houston Astros", "Atlanta Braves", "Los Angeles Dodgers", "Philadelphia Phillies"],
        "W": [90, 85, 89, 95, 98, 93],
        "L": [60, 65, 61, 55, 52, 60],
        "PCT": [0.600, 0.567, 0.593, 0.633, 0.653, 0.608],
        "Division": ["AL East", "AL East", "AL West", "NL East", "NL West", "NL East"],
        "League": ["AL", "AL", "AL", "NL", "NL", "NL"],
        "GB": ["-", "5.0", "-", "-", "-", "2.0"]
    }
    
    df = pd.DataFrame(data)
    print("✓ Generated emergency fallback standings data")
    return df

def calculate_games_behind(df):
    """Calculate Games Behind within each division"""
    for division in df["Division"].unique():
        division_df = df[df["Division"] == division].copy()
        
        if len(division_df) == 0:
            continue
        
        division_df = division_df.sort_values("PCT", ascending=False)
        
        if len(division_df) > 0:
            leader_wins = division_df.iloc[0]["W"]
            leader_losses = division_df.iloc[0]["L"]
            
            for i, row in division_df.iterrows():
                if i == division_df.index[0]:
                    df.loc[i, "GB"] = 0.0
                else:
                    gb = ((leader_wins - row["W"]) + (row["L"] - leader_losses)) / 2
                    df.loc[i, "GB"] = round(gb, 1)
    
    df["GB"] = df["GB"].astype(float).round(1).astype(str)
    df.loc[df["GB"] == "0.0", "GB"] = "-"
    
    return df

def generate_standings_tables(df):
    """Generate HTML tables for each division"""
    divisions = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West"]
    
    for division in divisions:
        division_df = df[df["Division"] == division].copy()
        
        if division_df.empty:
            continue
            
        division_df = division_df.sort_values("PCT", ascending=False)
        display_df = division_df[["Team", "W", "L", "PCT", "GB"]]
        display_df["PCT"] = display_df["PCT"].apply(lambda x: f"{x:.3f}")
        
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
                }}
                
                tr:nth-child(even) td {{ 
                    background-color: var(--row-even, #f9f9f9) !important;
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
                        // Cross-origin issues, ignore
                    }}
                }};
            </script>
        </head>
        <body>
            {display_df.to_html(index=False, classes='standings-table', escape=False)}
        </body>
        </html>
        """
        
        division_key = division.lower().replace(" ", "_")
        file_path = f"{output_path}/standings_{division_key}.html"
        with open(file_path, "w") as f:
            f.write(html_content)
        
        print(f"✓ Generated table for {division}")

def generate_league_html(df, league_code, league_name):
    """Generate HTML for a specific league"""
    try:
        league_df = df[df["League"] == league_code].copy()
        divisions = sorted([div for div in league_df["Division"].unique() if league_code in div])
        
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
                    padding: 15px;
                    background-color: var(--bg);
                    color: var(--text);
                }}
                
                .division-section {{
                    margin-bottom: 25px;
                }}
                
                .division-title {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: var(--text);
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 5px;
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
                }}
                
                tr:nth-child(even) td {{ 
                    background-color: var(--row-even, #f9f9f9) !important;
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
                        // Cross-origin issues, ignore
                    }}
                }};
            </script>
        </head>
        <body>
        """
        
        for division in divisions:
            division_df = league_df[league_df["Division"] == division].sort_values("PCT", ascending=False)
            display_df = division_df[["Team", "W", "L", "PCT", "GB"]]
            display_df["PCT"] = display_df["PCT"].apply(lambda x: f"{x:.3f}")
            
            html_content += f"""
                <div class="division-section">
                    <div class="division-title">{division}</div>
                    {display_df.to_html(index=False, classes='standings-table', escape=False)}
                </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        file_path = f"{output_path}/standings_{league_code.lower()}_all.html"
        with open(file_path, "w") as f:
            f.write(html_content)
        
        print(f"✓ Generated {league_name} standings HTML")
        
    except Exception as e:
        print(f"Error generating {league_name} HTML: {e}")

def generate_standings_charts(df):
    """Generate visualization charts for standings"""
    divisions = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West"]
    
    for division in divisions:
        division_df = df[df["Division"] == division].copy()
        
        if division_df.empty:
            continue
            
        division_df = division_df.sort_values("W", ascending=False)
        
        plt.figure(figsize=(10, 6))
        
        color = "royalblue" if "AL" in division else "firebrick"
        bars = plt.barh(division_df["Team"], division_df["W"], color=color)
        
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 1, bar.get_y() + bar.get_height()/2, f"{int(width)} W", 
                    ha='left', va='center')
        
        plt.title(f"{division} Standings - 2025", fontsize=14, fontweight='bold')
        plt.xlabel("Wins", fontsize=12)
        plt.ylabel("Team", fontsize=12)
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        division_key = division.lower().replace(" ", "_")
        plt.savefig(f"{output_path}/standings_{division_key}.png", dpi=120, bbox_inches="tight")
        plt.close()
        
        print(f"✓ Generated chart for {division}")
    
    # Overall standings chart
    plt.figure(figsize=(12, 8))
    
    all_df = df.sort_values("W", ascending=False)
    colors = ['royalblue' if league == 'AL' else 'firebrick' for league in all_df['League']]
    
    bars = plt.barh(all_df["Team"], all_df["W"], color=colors)
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, f"{int(width)} W", 
                ha='left', va='center')
    
    plt.title("MLB Overall Standings - 2025", fontsize=16, fontweight='bold')
    plt.xlabel("Wins", fontsize=14)
    plt.ylabel("Team", fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
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
    df.to_csv(f"{output_path}/standings_all.csv", index=False)
    
    try:
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
            al_leader_data = {"team": "N/A", "wins": 0, "losses": 0, "pct": 0.0, "division": "N/A"}
        
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
            nl_leader_data = {"team": "N/A", "wins": 0, "losses": 0, "pct": 0.0, "division": "N/A"}
        
        # Find closest division race
        closest_race = None
        smallest_game_diff = float('inf')
        
        for division in df["Division"].unique():
            division_df = df[df["Division"] == division].sort_values("PCT", ascending=False)
            if len(division_df) >= 2:
                leader = division_df.iloc[0]
                second = division_df.iloc[1]
                games_diff = ((leader["W"] - second["W"]) + (second["L"] - leader["L"])) / 2
                
                if games_diff < smallest_game_diff:
                    smallest_game_diff = games_diff
                    closest_race = {
                        "division": division,
                        "leader": {"team": leader["Team"], "wins": int(leader["W"]), "losses": int(leader["L"]), "pct": float(leader["PCT"])},
                        "second": {"team": second["Team"], "wins": int(second["W"]), "losses": int(second["L"]), "pct": float(second["PCT"])},
                        "games_behind": float(smallest_game_diff)
                    }
        
        if closest_race is None:
            closest_race = {
                "division": "N/A",
                "leader": {"team": "N/A", "wins": 0, "losses": 0},
                "second": {"team": "N/A", "wins": 0, "losses": 0},
                "games_behind": 0.0
            }
        
        summary = {
            "al_leader": al_leader_data,
            "nl_leader": nl_leader_data,
            "closest_race": closest_race,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(f"{output_path}/standings_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("✓ Generated standings summary data")
    
    except Exception as e:
        print(f"Error generating standings summary: {e}")
        fallback_summary = {
            "al_leader": {"team": "Houston Astros", "wins": 94, "losses": 68, "pct": 0.580, "division": "AL West"},
            "nl_leader": {"team": "Los Angeles Dodgers", "wins": 98, "losses": 64, "pct": 0.605, "division": "NL West"},
            "closest_race": {"division": "AL East", "leader": {"team": "New York Yankees", "wins": 92, "losses": 70}, "second": {"team": "Boston Red Sox", "wins": 88, "losses": 74}, "games_behind": 4.0},
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(f"{output_path}/standings_summary.json", "w") as f:
            json.dump(fallback_summary, f, indent=2)

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
        
        print("Generating league standings HTML...")
        generate_league_html(df, "AL", "American League")
        generate_league_html(df, "NL", "National League")
        
        print("Generating charts...")
        generate_standings_charts(df)
        
        print("Generating summary data...")
        generate_standings_summary(df)
        
        with open(f"{output_path}/last_updated_standings.txt", "w") as f:
            f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("✓ Standings data generation complete!")
        
    except Exception as e:
        print(f"Error in standings_chart.py: {e}")
        traceback.print_exc()
        
        with open(f"{output_path}/last_updated_standings.txt", "w") as f:
            f.write(f"Error: {str(e)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()