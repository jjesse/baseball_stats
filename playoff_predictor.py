import pandas as pd
import json
import os
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)


def calculate_team_strength():
    """Calculate team strength metrics for playoff predictions"""
    try:
        # Load current standings data
        standings_file = f"{output_path}/standings_all.csv"
        if not os.path.exists(standings_file):
            print("Standings data not found, using fallback calculations")
            return get_fallback_team_strength()

        df = pd.read_csv(standings_file)

        # Calculate team strength metrics
        team_strength = {}

        for _, team in df.iterrows():
            team_name = team.get("Team", team.get("Tm", "Unknown"))
            wins = int(team.get("W", 0))
            losses = int(team.get("L", 0))
            games_played = wins + losses

            if games_played > 0:
                win_pct = wins / games_played
                # Project to 162 games
                projected_wins = win_pct * 162

                # Calculate strength score (combination of current performance and projected wins)
                strength_score = (win_pct * 0.7) + ((projected_wins - 81) / 81 * 0.3)

                team_strength[team_name] = {
                    "wins": wins,
                    "losses": losses,
                    "win_pct": round(win_pct, 3),
                    "projected_wins": round(projected_wins, 1),  # Project to 162 games
                    "strength_score": round(strength_score, 3),  # Overall team strength
                    "games_remaining": 162 - games_played,
                    "division": team.get("Division", "unknown"),
                }

        return team_strength

    except Exception as e:
        print(f"Error calculating team strength: {e}")
        return get_fallback_team_strength()


def get_fallback_team_strength():
    """Fallback team strength data based on current 2025 season"""
    return {
        # AL East
        "New York Yankees": {
            "wins": 48,
            "losses": 47,
            "win_pct": 0.505,
            "projected_wins": 81.8,
            "strength_score": 0.51,
            "games_remaining": 67,
            "division": "al_east",
        },
        "Tampa Bay Rays": {
            "wins": 47,
            "losses": 48,
            "win_pct": 0.495,
            "projected_wins": 80.2,
            "strength_score": 0.49,
            "games_remaining": 67,
            "division": "al_east",
        },
        "Toronto Blue Jays": {
            "wins": 45,
            "losses": 50,
            "win_pct": 0.474,
            "projected_wins": 76.8,
            "strength_score": 0.47,
            "games_remaining": 67,
            "division": "al_east",
        },
        "Boston Red Sox": {
            "wins": 41,
            "losses": 54,
            "win_pct": 0.432,
            "projected_wins": 69.9,
            "strength_score": 0.43,
            "games_remaining": 67,
            "division": "al_east",
        },
        "Baltimore Orioles": {
            "wins": 38,
            "losses": 57,
            "win_pct": 0.400,
            "projected_wins": 64.8,
            "strength_score": 0.40,
            "games_remaining": 67,
            "division": "al_east",
        },
        # AL Central
        "Detroit Tigers": {
            "wins": 53,
            "losses": 42,
            "win_pct": 0.558,
            "projected_wins": 90.4,
            "strength_score": 0.67,
            "games_remaining": 67,
            "division": "al_central",
        },
        "Cleveland Guardians": {
            "wins": 52,
            "losses": 43,
            "win_pct": 0.547,
            "projected_wins": 88.6,
            "strength_score": 0.65,
            "games_remaining": 67,
            "division": "al_central",
        },
        "Minnesota Twins": {
            "wins": 44,
            "losses": 51,
            "win_pct": 0.463,
            "projected_wins": 75.0,
            "strength_score": 0.46,
            "games_remaining": 67,
            "division": "al_central",
        },
        "Kansas City Royals": {
            "wins": 39,
            "losses": 56,
            "win_pct": 0.411,
            "projected_wins": 66.6,
            "strength_score": 0.41,
            "games_remaining": 67,
            "division": "al_central",
        },
        "Chicago White Sox": {
            "wins": 25,
            "losses": 70,
            "win_pct": 0.263,
            "projected_wins": 42.6,
            "strength_score": 0.26,
            "games_remaining": 67,
            "division": "al_central",
        },
        # AL West
        "Houston Astros": {
            "wins": 51,
            "losses": 44,
            "win_pct": 0.537,
            "projected_wins": 86.9,
            "strength_score": 0.63,
            "games_remaining": 67,
            "division": "al_west",
        },
        "Seattle Mariners": {
            "wins": 47,
            "losses": 48,
            "win_pct": 0.495,
            "projected_wins": 80.2,
            "strength_score": 0.49,
            "games_remaining": 67,
            "division": "al_west",
        },
        "Texas Rangers": {
            "wins": 42,
            "losses": 53,
            "win_pct": 0.442,
            "projected_wins": 71.6,
            "strength_score": 0.44,
            "games_remaining": 67,
            "division": "al_west",
        },
        "Los Angeles Angels": {
            "wins": 38,
            "losses": 57,
            "win_pct": 0.400,
            "projected_wins": 64.8,
            "strength_score": 0.40,
            "games_remaining": 67,
            "division": "al_west",
        },
        "Oakland Athletics": {
            "wins": 37,
            "losses": 58,
            "win_pct": 0.389,
            "projected_wins": 63.0,
            "strength_score": 0.39,
            "games_remaining": 67,
            "division": "al_west",
        },
        # NL East
        "Philadelphia Phillies": {
            "wins": 54,
            "losses": 41,
            "win_pct": 0.568,
            "projected_wins": 92.0,
            "strength_score": 0.69,
            "games_remaining": 67,
            "division": "nl_east",
        },
        "Atlanta Braves": {
            "wins": 49,
            "losses": 46,
            "win_pct": 0.516,
            "projected_wins": 83.6,
            "strength_score": 0.54,
            "games_remaining": 67,
            "division": "nl_east",
        },
        "New York Mets": {
            "wins": 45,
            "losses": 50,
            "win_pct": 0.474,
            "projected_wins": 76.8,
            "strength_score": 0.47,
            "games_remaining": 67,
            "division": "nl_east",
        },
        "Washington Nationals": {
            "wins": 40,
            "losses": 55,
            "win_pct": 0.421,
            "projected_wins": 68.2,
            "strength_score": 0.42,
            "games_remaining": 67,
            "division": "nl_east",
        },
        "Miami Marlins": {
            "wins": 34,
            "losses": 61,
            "win_pct": 0.358,
            "projected_wins": 58.0,
            "strength_score": 0.36,
            "games_remaining": 67,
            "division": "nl_east",
        },
        # NL Central
        "Milwaukee Brewers": {
            "wins": 53,
            "losses": 42,
            "win_pct": 0.558,
            "projected_wins": 90.4,
            "strength_score": 0.67,
            "games_remaining": 67,
            "division": "nl_central",
        },
        "Chicago Cubs": {
            "wins": 47,
            "losses": 48,
            "win_pct": 0.495,
            "projected_wins": 80.2,
            "strength_score": 0.49,
            "games_remaining": 67,
            "division": "nl_central",
        },
        "St. Louis Cardinals": {
            "wins": 45,
            "losses": 50,
            "win_pct": 0.474,
            "projected_wins": 76.8,
            "strength_score": 0.47,
            "games_remaining": 67,
            "division": "nl_central",
        },
        "Cincinnati Reds": {
            "wins": 42,
            "losses": 53,
            "win_pct": 0.442,
            "projected_wins": 71.6,
            "strength_score": 0.44,
            "games_remaining": 67,
            "division": "nl_central",
        },
        "Pittsburgh Pirates": {
            "wins": 41,
            "losses": 54,
            "win_pct": 0.432,
            "projected_wins": 69.9,
            "strength_score": 0.43,
            "games_remaining": 67,
            "division": "nl_central",
        },
        # NL West
        "Los Angeles Dodgers": {
            "wins": 58,
            "losses": 37,
            "win_pct": 0.611,
            "projected_wins": 98.9,
            "strength_score": 0.76,
            "games_remaining": 67,
            "division": "nl_west",
        },
        "San Diego Padres": {
            "wins": 48,
            "losses": 47,
            "win_pct": 0.505,
            "projected_wins": 81.8,
            "strength_score": 0.51,
            "games_remaining": 67,
            "division": "nl_west",
        },
        "Arizona Diamondbacks": {
            "wins": 47,
            "losses": 48,
            "win_pct": 0.495,
            "projected_wins": 80.2,
            "strength_score": 0.49,
            "games_remaining": 67,
            "division": "nl_west",
        },
        "San Francisco Giants": {
            "wins": 44,
            "losses": 51,
            "win_pct": 0.463,
            "projected_wins": 75.0,
            "strength_score": 0.46,
            "games_remaining": 67,
            "division": "nl_west",
        },
        "Colorado Rockies": {
            "wins": 35,
            "losses": 60,
            "win_pct": 0.368,
            "projected_wins": 59.6,
            "strength_score": 0.37,
            "games_remaining": 67,
            "division": "nl_west",
        },
    }


def calculate_playoff_probabilities(team_strength):
    """Calculate playoff probabilities for each team"""
    playoff_scenarios = {
        "al_division_winners": {},  # 🏁 AL Division Championship Odds
        "nl_division_winners": {},  # 🏁 NL Division Championship Odds
        "al_wild_card": {},  # 🎟️ AL Wild Card Probabilities
        "nl_wild_card": {},  # 🎟️ NL Wild Card Probabilities
        "world_series_odds": {},  # 🏆 World Series Championship Odds
    }

    # Group teams by division
    divisions = {
        "al_east": [],
        "al_central": [],
        "al_west": [],
        "nl_east": [],
        "nl_central": [],
        "nl_west": [],
    }

    for team, stats in team_strength.items():
        division = stats["division"]
        if division in divisions:
            divisions[division].append((team, stats))

    # Calculate division winner probabilities
    for division, teams in divisions.items():
        if not teams:
            continue

        # Sort by projected wins
        teams.sort(key=lambda x: x[1]["projected_wins"], reverse=True)

        total_strength = sum(team[1]["strength_score"] for team in teams)

        for team, stats in teams:
            if total_strength > 0:
                # Division probability based on strength score and current lead
                base_prob = (stats["strength_score"] / total_strength) * 100

                # Adjust based on current wins lead
                leader_wins = teams[0][1]["wins"]
                wins_behind = leader_wins - stats["wins"]

                # Apply lead bonus/penalty
                if wins_behind == 0:  # Division leader
                    base_prob *= 1.3
                elif wins_behind <= 2:  # Close behind
                    base_prob *= 0.9
                elif wins_behind <= 5:  # Moderate deficit
                    base_prob *= 0.6
                else:  # Large deficit
                    base_prob *= 0.3

                # Cap probabilities
                division_prob = min(max(base_prob, 0.1), 85.0)

                if "al_" in division:
                    playoff_scenarios["al_division_winners"][team] = round(
                        division_prob, 1
                    )
                else:
                    playoff_scenarios["nl_division_winners"][team] = round(
                        division_prob, 1
                    )

    # Calculate Wild Card probabilities
    al_teams = [
        (team, stats)
        for team, stats in team_strength.items()
        if stats["division"].startswith("al_")
    ]
    nl_teams = [
        (team, stats)
        for team, stats in team_strength.items()
        if stats["division"].startswith("nl_")
    ]

    # AL Wild Card (top 3 non-division winners)
    al_teams.sort(key=lambda x: x[1]["projected_wins"], reverse=True)
    for i, (team, stats) in enumerate(al_teams):
        # Wild card probability decreases with ranking
        if i < 8:  # Top 8 teams have wild card chance
            wild_card_prob = max(0, 75 - (i * 12) - (90 - stats["projected_wins"]) * 2)
            playoff_scenarios["al_wild_card"][team] = round(wild_card_prob, 1)

    # NL Wild Card (top 3 non-division winners)
    nl_teams.sort(key=lambda x: x[1]["projected_wins"], reverse=True)
    for i, (team, stats) in enumerate(nl_teams):
        if i < 8:  # Top 8 teams have wild card chance
            wild_card_prob = max(0, 75 - (i * 12) - (90 - stats["projected_wins"]) * 2)
            playoff_scenarios["nl_wild_card"][team] = round(wild_card_prob, 1)

    # World Series odds calculation - THIS IS THE KEY FEATURE
    all_teams = list(team_strength.items())
    all_teams.sort(key=lambda x: x[1]["strength_score"], reverse=True)

    for i, (team, stats) in enumerate(all_teams[:12]):  # Top 12 teams get WS odds
        # World Series probability based on strength score and playoff position
        base_ws_prob = (stats["strength_score"] * 15) + (5 if i < 6 else 2)
        ws_prob = max(0.1, min(base_ws_prob, 25.0))
        playoff_scenarios["world_series_odds"][team] = round(ws_prob, 1)

    return playoff_scenarios


def create_playoff_visualizations(playoff_scenarios, team_strength):
    """Create charts for playoff scenarios"""
    try:
        # Create playoff probability chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            "2025 MLB Playoff Probability Tracker", fontsize=16, fontweight="bold"
        )

        # AL Division Winners
        al_div_teams = list(playoff_scenarios["al_division_winners"].keys())[:8]
        al_div_probs = [
            playoff_scenarios["al_division_winners"][team] for team in al_div_teams
        ]

        bars1 = ax1.barh(al_div_teams, al_div_probs, color="#1f77b4")
        ax1.set_title("AL Division Winner Probabilities")
        ax1.set_xlabel("Probability (%)")
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                ha="left",
                va="center",
            )

        # NL Division Winners
        nl_div_teams = list(playoff_scenarios["nl_division_winners"].keys())[:8]
        nl_div_probs = [
            playoff_scenarios["nl_division_winners"][team] for team in nl_div_teams
        ]

        bars2 = ax2.barh(nl_div_teams, nl_div_probs, color="#ff7f0e")
        ax2.set_title("NL Division Winner Probabilities")
        ax2.set_xlabel("Probability (%)")
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                ha="left",
                va="center",
            )

        # AL Wild Card
        al_wc_teams = list(playoff_scenarios["al_wild_card"].keys())[:6]
        al_wc_probs = [playoff_scenarios["al_wild_card"][team] for team in al_wc_teams]

        bars3 = ax3.barh(al_wc_teams, al_wc_probs, color="#2ca02c")
        ax3.set_title("AL Wild Card Probabilities")
        ax3.set_xlabel("Probability (%)")
        for i, bar in enumerate(bars3):
            width = bar.get_width()
            ax3.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                ha="left",
                va="center",
            )

        # NL Wild Card
        nl_wc_teams = list(playoff_scenarios["nl_wild_card"].keys())[:6]
        nl_wc_probs = [playoff_scenarios["nl_wild_card"][team] for team in nl_wc_teams]

        bars4 = ax4.barh(nl_wc_teams, nl_wc_probs, color="#d62728")
        ax4.set_title("NL Wild Card Probabilities")
        ax4.set_xlabel("Probability (%)")
        for i, bar in enumerate(bars4):
            width = bar.get_width()
            ax4.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                ha="left",
                va="center",
            )

        plt.tight_layout()
        plt.savefig(
            f"{output_path}/playoff_probabilities_chart.png",
            dpi=150,
            bbox_inches="tight",
        )
        plt.close()

        # Create World Series odds chart
        plt.figure(figsize=(14, 8))
        ws_teams = list(playoff_scenarios["world_series_odds"].keys())[:10]
        ws_odds = [playoff_scenarios["world_series_odds"][team] for team in ws_teams]

        # Color teams by league
        colors = []
        for team in ws_teams:
            division = team_strength.get(team, {}).get("division", "")
            if division.startswith("al_"):
                colors.append("#1f77b4")  # Blue for AL
            else:
                colors.append("#ff7f0e")  # Orange for NL

        bars = plt.barh(ws_teams, ws_odds, color=colors)
        plt.title("2025 World Series Championship Odds", fontsize=14, fontweight="bold")
        plt.xlabel("Probability (%)")

        # Add percentage labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(
                width + 0.2,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                ha="left",
                va="center",
            )

        # Add legend
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor="#1f77b4", label="American League"),
            Patch(facecolor="#ff7f0e", label="National League"),
        ]
        plt.legend(handles=legend_elements, loc="lower right")

        plt.tight_layout()
        plt.savefig(
            f"{output_path}/world_series_odds_chart.png", dpi=150, bbox_inches="tight"
        )
        plt.close()

        print("✓ Playoff visualization charts created successfully")

    except Exception as e:
        print(f"Error creating playoff visualizations: {e}")


def generate_playoff_summary():
    """Generate summary insights about playoff races"""
    team_strength = calculate_team_strength()
    playoff_scenarios = calculate_playoff_probabilities(team_strength)

    # Generate insights
    insights = {
        "closest_division_races": [],  # 🔥 Hottest division battles
        "wild_card_battles": [],  # 🎟️ Wild card race analysis
        "world_series_favorites": [],  # 🏆 Championship contenders
        "elimination_watch": [],  # ⚠️ Teams in trouble
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # World Series favorites - TOP FEATURE
    ws_favorites = sorted(
        playoff_scenarios["world_series_odds"].items(), key=lambda x: x[1], reverse=True
    )[:5]
    insights["world_series_favorites"] = [
        {"team": team, "odds": odds} for team, odds in ws_favorites
    ]

    # Find closest division races
    divisions = ["al_east", "al_central", "al_west", "nl_east", "nl_central", "nl_west"]
    for division in divisions:
        div_teams = [
            (team, stats)
            for team, stats in team_strength.items()
            if stats["division"] == division
        ]
        if len(div_teams) >= 2:
            div_teams.sort(key=lambda x: x[1]["wins"], reverse=True)
            leader = div_teams[0]
            second = div_teams[1]
            gap = leader[1]["wins"] - second[1]["wins"]

            if gap <= 5:  # Close race
                insights["closest_division_races"].append(
                    {
                        "division": division.replace("_", " ").title(),
                        "leader": leader[0],
                        "leader_wins": leader[1]["wins"],
                        "second": second[0],
                        "second_wins": second[1]["wins"],
                        "gap": gap,
                    }
                )

    # Wild Card battles
    al_wc_contenders = sorted(
        playoff_scenarios["al_wild_card"].items(), key=lambda x: x[1], reverse=True
    )[:6]
    nl_wc_contenders = sorted(
        playoff_scenarios["nl_wild_card"].items(), key=lambda x: x[1], reverse=True
    )[:6]

    insights["wild_card_battles"] = {
        "al_contenders": [
            {"team": team, "probability": prob} for team, prob in al_wc_contenders
        ],
        "nl_contenders": [
            {"team": team, "probability": prob} for team, prob in nl_wc_contenders
        ],
    }

    return insights, playoff_scenarios, team_strength


if __name__ == "__main__":
    try:
        # Generate all playoff predictions
        insights, playoff_scenarios, team_strength = generate_playoff_summary()

        # Save playoff data
        with open(f"{output_path}/playoff_predictions.json", "w") as f:
            json.dump(
                {
                    "insights": insights,
                    "playoff_scenarios": playoff_scenarios,
                    "team_strength": team_strength,
                },
                f,
                indent=2,
            )

        # Create visualizations
        create_playoff_visualizations(playoff_scenarios, team_strength)

        print("✓ Playoff predictions and visualizations generated successfully!")
    except Exception as e:
        print(f"Error generating playoff predictions: {e}")
        # Create minimal fallback
        fallback_data = {
            "insights": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "closest_division_races": [],
                "wild_card_battles": [],
                "world_series_favorites": [],
            },
            "playoff_scenarios": {
                "al_division_winners": {},
                "nl_division_winners": {},
                "al_wild_card": {},
                "nl_wild_card": {},
                "world_series_odds": {},
            },
            "team_strength": {},
        }

        with open(f"{output_path}/playoff_predictions.json", "w") as f:
            json.dump(fallback_data, f, indent=2)

        raise
