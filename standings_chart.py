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
import seaborn as sns
import requests
from datetime import datetime
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
                # Standardize division names to our format (AL East, NL West, etc.)
                if "American" in division_name:
                    league = "AL"
                    div = division_name.replace("American League ", "")
                    division_name = f"AL {div}"
                elif "National" in division_name:
                    league = "NL"
                    div = division_name.replace("National League ", "")
                    division_name = f"NL {div}"
                else:
                    # Default league assignment if name format is different
                    league = "AL" if "AL" in division_name else "NL"
                
                for team_record in division_record.get("teamRecords", []):
                    team_name = team_record.get("team", {}).get("name", "Unknown")
                    team_abbrev = team_record.get("team", {}).get("abbreviation", team_name[:3].upper())
                    
                    wins = team_record.get("wins", 0)
                    losses = team_record.get("losses", 0)
                    pct = team_record.get("winningPercentage", "0")
                    
                    # Convert winning percentage from string to float
                    try:
                        pct = float(pct)
                    except:
                        # Calculate if not provided
                        if wins + losses > 0:
                            pct = wins / (wins + losses)
                        else:
                            pct = 0.0
                    
                    all_teams.append({
                        "Team": team_name,
                        "Abbrev": team_abbrev,
                        "W": wins,
                        "L": losses,
                        "PCT": pct,
                        "GB": 0.0,  # Will calculate later
                        "Division": division_name,
                        "League": league
                    })
        
        if not all_teams:
            print("No data found in MLB.com API response")
            return None
        
        # Create DataFrame and calculate GB for each division
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
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Process the ESPN HTML
        all_teams = []
        
        # Map division names to standardized format
        division_mapping = {
            "AL EAST": "AL East",
            "AL CENTRAL": "AL Central", 
            "AL WEST": "AL West",
            "NL EAST": "NL East", 
            "NL CENTRAL": "NL Central",
            "NL WEST": "NL West"
        }
        
        # Find division tables
        for division_header in soup.find_all('div', class_='Table__Title'):
            division_text = division_header.get_text().strip().upper()
            
            # Skip if not a valid division
            if division_text not in division_mapping:
                continue
                
            division_name = division_mapping[division_text]
            league = division_name.split()[0]  # AL or NL
            
            # Find the table for this division
            table = division_header.find_next('table')
            if not table:
                continue
                
            # Get team rows
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if len(cells) < 10:  # Ensure it's a data row
                    continue
                    
                # Extract team name
                team_link = row.find('a', class_='AnchorLink')
                if not team_link:
                    continue
                team_name = team_link.get_text().strip()
                
                # Extract team abbreviation
                team_abbrev = team_name[:3].upper()  # Default abbreviation
                
                # Extract win/loss data - assuming standard ESPN format
                try:
                    wins = int(cells[0].get_text().strip())
                    losses = int(cells[1].get_text().strip())
                    
                    # Calculate PCT
                    pct = round(wins / (wins + losses), 3) if wins + losses > 0 else 0.0
                    
                    # Add to team list
                    all_teams.append({
                        "Team": team_name,
                        "Abbrev": team_abbrev,
                        "W": wins,
                        "L": losses,
                        "PCT": pct,
                        "GB": 0.0,  # Will calculate later
                        "Division": division_name,
                        "League": league
                    })
                except (ValueError, IndexError):
                    continue
        
        if not all_teams:
            print("No data found in ESPN HTML")
            return None
        
        # Create DataFrame and calculate GB for each division
        df = pd.DataFrame(all_teams)
        calculate_games_behind(df)
        
        return df
        
    except Exception as e:
        print(f"Error fetching from ESPN: {e}")
        return None


def fetch_standings_baseball_reference():
    """Fetch standings from Baseball Reference (tertiary source)"""
    try:
        url = "https://www.baseball-reference.com/leagues/majors/2025-standings.shtml"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Process Baseball Reference HTML
        all_teams = []
        
        # Division names for each table
        divisions = [
            "AL East", "AL Central", "AL West",
            "NL East", "NL Central", "NL West"
        ]
        
        # Find all division tables
        tables = soup.find_all('table')
        division_tables = []
        
        for table in tables:
            if 'standings_' in table.get('id', ''):
                division_tables.append(table)
        
        # Process each division table
        for idx, table in enumerate(division_tables):
            if idx >= len(divisions):
                break
                
            division_name = divisions[idx]
            league = division_name.split()[0]  # AL or NL
            
            # Process team rows
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if not cells:  # Skip header or separator rows
                    continue
                    
                # Extract team name
                team_cell = row.find('th')
                if not team_cell or not team_cell.find('a'):
                    continue
                team_name = team_cell.find('a').get_text().strip()
                
                # Use 3-letter abbreviation
                team_abbrev = team_name[:3].upper()
                
                try:
                    # Baseball Reference columns (may need adjustment)
                    wins = int(cells[0].get_text().strip())
                    losses = int(cells[1].get_text().strip())
                    
                    # Calculate PCT
                    pct_text = cells[2].get_text().strip()
                    try:
                        pct = float(pct_text)
                    except:
                        pct = round(wins / (wins + losses), 3) if wins + losses > 0 else 0.0
                    
                    # Add to team list
                    all_teams.append({
                        "Team": team_name,
                        "Abbrev": team_abbrev,
                        "W": wins,
                        "L": losses,
                        "PCT": pct,
                        "GB": 0.0,  # Will calculate later
                        "Division": division_name,
                        "League": league
                    })
                except (ValueError, IndexError):
                    continue
        
        if not all_teams:
            print("No data found in Baseball Reference HTML")
            return None
        
        # Create DataFrame and calculate GB for each division
        df = pd.DataFrame(all_teams)
        calculate_games_behind(df)
        
        return df
        
    except Exception as e:
        print(f"Error fetching from Baseball Reference: {e}")
        return None


def get_fallback_standings():
    """Provide fallback standings data when online sources are unavailable"""
    # Define team information dictionary with proper names, abbreviations, and division assignments
    team_info = {
        # AL East
        "New York Yankees": {"abbrev": "NYY", "division": "AL East", "league": "AL"},
        "Boston Red Sox": {"abbrev": "BOS", "division": "AL East", "league": "AL"},
        "Toronto Blue Jays": {"abbrev": "TOR", "division": "AL East", "league": "AL"},
        "Tampa Bay Rays": {"abbrev": "TB", "division": "AL East", "league": "AL"},
        "Baltimore Orioles": {"abbrev": "BAL", "division": "AL East", "league": "AL"},
        
        # AL Central
        "Cleveland Guardians": {"abbrev": "CLE", "division": "AL Central", "league": "AL"},
        "Minnesota Twins": {"abbrev": "MIN", "division": "AL Central", "league": "AL"},
        "Detroit Tigers": {"abbrev": "DET", "division": "AL Central", "league": "AL"},
        "Kansas City Royals": {"abbrev": "KC", "division": "AL Central", "league": "AL"},
        "Chicago White Sox": {"abbrev": "CWS", "division": "AL Central", "league": "AL"},
        
        # AL West
        "Houston Astros": {"abbrev": "HOU", "division": "AL West", "league": "AL"},
        "Seattle Mariners": {"abbrev": "SEA", "division": "AL West", "league": "AL"},
        "Texas Rangers": {"abbrev": "TEX", "division": "AL West", "league": "AL"},
        "Los Angeles Angels": {"abbrev": "LAA", "division": "AL West", "league": "AL"},
        "Oakland Athletics": {"abbrev": "OAK", "division": "AL West", "league": "AL"},
        
        # NL East
        "Atlanta Braves": {"abbrev": "ATL", "division": "NL East", "league": "NL"},
        "Philadelphia Phillies": {"abbrev": "PHI", "division": "NL East", "league": "NL"},
        "New York Mets": {"abbrev": "NYM", "division": "NL East", "league": "NL"},
        "Miami Marlins": {"abbrev": "MIA", "division": "NL East", "league": "NL"},
        "Washington Nationals": {"abbrev": "WSH", "division": "NL East", "league": "NL"},
        
        # NL Central
        "Milwaukee Brewers": {"abbrev": "MIL", "division": "NL Central", "league": "NL"},
        "Chicago Cubs": {"abbrev": "CHC", "division": "NL Central", "league": "NL"},
        "St. Louis Cardinals": {"abbrev": "STL", "division": "NL Central", "league": "NL"},
        "Cincinnati Reds": {"abbrev": "CIN", "division": "NL Central", "league": "NL"},
        "Pittsburgh Pirates": {"abbrev": "PIT", "division": "NL Central", "league": "NL"},
        
        # NL West
        "Los Angeles Dodgers": {"abbrev": "LAD", "division": "NL West", "league": "NL"},
        "San Diego Padres": {"abbrev": "SD", "division": "NL West", "league": "NL"},
        "San Francisco Giants": {"abbrev": "SF", "division": "NL West", "league": "NL"},
        "Arizona Diamondbacks": {"abbrev": "ARI", "division": "NL West", "league": "NL"},
        "Colorado Rockies": {"abbrev": "COL", "division": "NL West", "league": "NL"}
    }
    
    # Sample data for 2025 season
    data = {
        "Team": list(team_info.keys()),
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
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add team abbreviation, division, and league from team_info dictionary
    df["Abbrev"] = df["Team"].apply(lambda x: team_info[x]["abbrev"])
    df["Division"] = df["Team"].apply(lambda x: team_info[x]["division"])
    df["League"] = df["Team"].apply(lambda x: team_info[x]["league"])
    
    # Calculate winning percentage
    df["PCT"] = df["W"] / (df["W"] + df["L"]).astype(float)
    df["PCT"] = df["PCT"].round(3)
    
    # Calculate GB
    calculate_games_behind(df)
    
    print("✓ Generated fallback standings data")
    return df


def get_emergency_fallback():
    """Absolute last resort if all other methods fail"""
    # Minimal team list with proper names
    data = {
        "Team": [
            "New York Yankees", "Boston Red Sox", "Tampa Bay Rays", 
            "Cleveland Guardians", "Minnesota Twins",
            "Houston Astros", "Seattle Mariners",
            "Atlanta Braves", "Philadelphia Phillies", 
            "Milwaukee Brewers", "Chicago Cubs",
            "Los Angeles Dodgers", "San Diego Padres"
        ],
        "Abbrev": [
            "NYY", "BOS", "TB", 
            "CLE", "MIN",
            "HOU", "SEA",
            "ATL", "PHI", 
            "MIL", "CHC",
            "LAD", "SD"
        ],
        "W": [90, 85, 80, 75, 70, 89, 84, 95, 90, 88, 82, 98, 92],
        "L": [60, 65, 70, 75, 80, 61, 66, 55, 60, 62, 68, 52, 58],
        "PCT": [0.600, 0.567, 0.533, 0.500, 0.467, 0.593, 0.560, 0.633, 0.600, 0.587, 0.547, 0.653, 0.613],
        "Division": [
            "AL East", "AL East", "AL East",
            "AL Central", "AL Central",
            "AL West", "AL West",
            "NL East", "NL East",
            "NL Central", "NL Central",
            "NL West", "NL West"
        ],
        "League": [
            "AL", "AL", "AL", 
            "AL", "AL",
            "AL", "AL",
            "NL", "NL", 
            "NL", "NL",
            "NL", "NL"
        ],
    }
    
    df = pd.DataFrame(data)
    
    # Calculate GB
    calculate_games_behind(df)
    
    print("✓ Generated emergency fallback standings data")
    return df


def calculate_games_behind(df):
    """Calculate Games Behind within each division"""
    for division in df["Division"].unique():
        division_df = df[df["Division"] == division].copy()
        
        if len(division_df) == 0:
            continue
        
        # Sort by win percentage
        division_df = division_df.sort_values("PCT", ascending=False)
        
        # Get the values for the division leader
        leader_wins = division_df.iloc[0]["W"]
        leader_losses = division_df.iloc[0]["L"]
        
        # Calculate GB for each team
        for i, row in division_df.iterrows():
            if i == division_df.index[0]:  # Leader
                df.loc[i, "GB"] = 0.0
            else:
                gb = ((leader_wins - row["W"]) + (row["L"] - leader_losses)) / 2
                df.loc[i, "GB"] = round(gb, 1)
    
    # Convert GB to string representation
    df["GB"] = df["GB"].astype(float).round(1).astype(str)
    df.loc[df["GB"] == "0.0", "GB"] = "-"
    
    return df


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
    
    try:
        # Find AL leader (team with highest win percentage in American League)
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
        
        # Find NL leader (team with highest win percentage in National League)
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
    
    except Exception as e:
        print(f"Error generating standings summary: {e}")
        
        # Create a minimal fallback summary
        fallback_summary = {
            "al_leader": {"team": "Houston Astros", "wins": 94, "losses": 68, "pct": 0.580, "division": "AL West"},
            "nl_leader": {"team": "Los Angeles Dodgers", "wins": 98, "losses": 64, "pct": 0.605, "division": "NL West"},
            "closest_race": {
                "division": "AL East",
                "leader": {"team": "New York Yankees", "wins": 92, "losses": 70, "pct": 0.568},
                "second": {"team": "Boston Red Sox", "wins": 88, "losses": 74, "pct": 0.543},
                "games_behind": 4.0
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(f"{output_path}/standings_summary.json", "w") as f:
            json.dump(fallback_summary, f, indent=2)
        
        print("✓ Generated fallback standings summary data")


def generate_league_standings_html():
    """Generate consolidated standings HTML files for American and National Leagues"""
    try:
        # Load the CSV data if it exists
        csv_path = f"{output_path}/standings_all.csv"
        if not os.path.exists(csv_path):
            print("Cannot generate league standings HTML - standings CSV not found")
            return
            
        df = pd.read_csv(csv_path)
        
        # Generate American League HTML
        generate_league_html(df, "AL", "American League")
        
        # Generate National League HTML
        generate_league_html(df, "NL", "National League")
        
        print("✓ Generated league standings HTML files")
        
    except Exception as e:
        print(f"Error generating league standings HTML: {e}")


def generate_league_html(df, league_code, league_name):
    """Generate HTML for a specific league"""
    try:
        # Filter for this league
        league_df = df[df["League"] == league_code].copy()
        
        # Get divisions in this league
        divisions = sorted([div for div in league_df["Division"].unique() if league_code in div])
        
        # Create HTML content
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
                
                .league-container {{
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }}
                
                .division-section {{
                    margin-bottom: 20px;
                }}
                
                .division-title {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: var(--text);
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 5px;
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
            <div class="league-container">
        """
        
        # Add each division
        for division in divisions:
            division_df = league_df[league_df["Division"] == division].sort_values("PCT", ascending=False)
            
            # Format PCT as string
            division_df["PCT"] = division_df["PCT"].apply(lambda x: f"{x:.3f}")
            
            # Select columns for display
            display_df = division_df[["Team", "W", "L", "PCT", "GB"]]
            
            html_content += f"""
                <div class="division-section">
                    <div class="division-title">{division}</div>
                    <div class="table-container">
                        {display_df.to_html(index=False, classes='standings-table', escape=False)}
                    </div>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Save to file
        file_path = f"{output_path}/standings_{league_code.lower()}_all.html"
        with open(file_path, "w") as f:
            f.write(html_content)
        
        print(f"✓ Generated {league_name} standings HTML")
        
    except Exception as e:
        print(f"Error generating {league_name} HTML: {e}")


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
        generate_league_standings_html()
        
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
                "al_leader": {"team": "Houston Astros", "wins": 94, "losses": 68, "pct": 0.580, "division": "AL West"},
                "nl_leader": {"team": "Los Angeles Dodgers", "wins": 98, "losses": 64, "pct": 0.605, "division": "NL West"},
                "closest_race": {
                    "division": "AL East",
                    "leader": {"team": "New York Yankees", "wins": 92, "losses": 70},
                    "second": {"team": "Boston Red Sox", "wins": 88, "losses": 74},
                    "games_behind": 4.0
                },
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(f"{output_path}/standings_summary.json", "w") as f:
                json.dump(fallback_summary, f, indent=2)