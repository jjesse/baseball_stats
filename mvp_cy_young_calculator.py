import pandas as pd
import json
import os
from datetime import datetime
from pybaseball import batting_stats, pitching_stats

# Ensure output directory exists
output_path = os.environ.get("OUTPUT_PATH", "docs")
os.makedirs(output_path, exist_ok=True)


def calculate_mvp_predictions():
    """Calculate MVP predictions based on current stats"""
    try:
        df = batting_stats(2025)

        # Validate required columns exist
        required_cols = ["Name", "Team", "HR", "RBI", "AVG"]
        optional_cols = ["wRC+", "SB", "OPS", "wOBA", "AB", "OBP", "SLG"]

        # Check which columns are available
        available_cols = [
            col for col in required_cols + optional_cols if col in df.columns
        ]
        missing_required = [col for col in required_cols if col not in df.columns]

        if missing_required:
            print(
                f"Warning: Missing required columns for MVP calculation: {missing_required}"
            )
            return None, None

        # Filter by minimum at-bats if available
        if "AB" in df.columns:
            df = df[df["AB"] >= 50]  # Minimum playing time

        # Enhanced MVP scoring with available metrics
        mvp_score = 0

        # Core stats (always required)
        mvp_score += df["HR"] * 0.2  # Home runs
        mvp_score += df["RBI"] * 0.15  # RBIs
        mvp_score += df["AVG"] * 100 * 0.1  # Batting average

        # Advanced stats (if available)
        if "wRC+" in df.columns:
            mvp_score += df["wRC+"] * 0.25
        elif "OPS" in df.columns:
            mvp_score += df["OPS"] * 50 * 0.25

        if "SB" in df.columns:
            mvp_score += df["SB"] * 0.1

        if "wOBA" in df.columns:
            mvp_score += df["wOBA"] * 50 * 0.2
        elif "OBP" in df.columns and "SLG" in df.columns:
            mvp_score += (df["OBP"] + df["SLG"]) * 25 * 0.2

        df["MVP_Score"] = mvp_score

        # Add probability calculation
        if df["MVP_Score"].max() > 0:
            df["MVP_Probability"] = (
                df["MVP_Score"] / df["MVP_Score"].max() * 100
            ).round(1)
        else:
            df["MVP_Probability"] = 0

        # Create key stats column for display
        df["Key_Stats"] = df.apply(
            lambda row: f"{row['HR']}HR/{row['RBI']}RBI/{row['AVG']:.3f}AVG", axis=1
        )

        # Separate by league
        al_teams = [
            "NYY",
            "BOS",
            "TOR",
            "TB",
            "BAL",
            "CLE",
            "DET",
            "KC",
            "CWS",
            "MIN",
            "HOU",
            "LAA",
            "OAK",
            "SEA",
            "TEX",
        ]

        al_mvp = df[df["Team"].isin(al_teams)].nlargest(10, "MVP_Score")
        nl_mvp = df[~df["Team"].isin(al_teams)].nlargest(10, "MVP_Score")

        # Save predictions
        if not al_mvp.empty:
            al_mvp.to_csv(f"{output_path}/al_mvp_predictions.csv", index=False)
        if not nl_mvp.empty:
            nl_mvp.to_csv(f"{output_path}/nl_mvp_predictions.csv", index=False)

        return al_mvp, nl_mvp

    except Exception as e:
        print(f"Error calculating MVP predictions: {e}")
        return None, None


def calculate_cy_young_predictions():
    """Calculate Cy Young predictions based on current stats"""
    try:
        df = pitching_stats(2025)

        # Validate required columns exist
        required_cols = ["Name", "Team", "ERA", "W"]
        optional_cols = ["WHIP", "SO", "FIP", "K/BB", "IP", "G", "GS"]

        # Check which columns are available
        available_cols = [
            col for col in required_cols + optional_cols if col in df.columns
        ]
        missing_required = [col for col in required_cols if col not in df.columns]

        if missing_required:
            print(
                f"Warning: Missing required columns for Cy Young calculation: {missing_required}"
            )
            return None, None

        # Filter by minimum innings if available
        if "IP" in df.columns:
            df = df[df["IP"] >= 50]  # Minimum innings pitched

        # Enhanced Cy Young scoring with available metrics
        cy_score = 0

        # Traditional stats
        cy_score += (5.0 - df["ERA"].clip(upper=5.0)) * 25  # ERA (capped at 5.0)
        cy_score += df["W"] * 8  # Wins

        # Advanced stats (if available)
        if "WHIP" in df.columns:
            cy_score += (2.0 - df["WHIP"].clip(upper=2.0)) * 35
        if "SO" in df.columns:
            cy_score += df["SO"] * 0.15
        if "FIP" in df.columns:
            cy_score += (5.0 - df["FIP"].clip(upper=5.0)) * 20

        df["CY_Score"] = cy_score

        # Add probability calculation
        if df["CY_Score"].max() > 0:
            df["CyYoung_Probability"] = (
                df["CY_Score"] / df["CY_Score"].max() * 100
            ).round(1)
        else:
            df["CyYoung_Probability"] = 0

        # Create key stats column for display
        df["Key_Stats"] = df.apply(
            lambda row: f"{row['W']}W/{row['ERA']:.2f}ERA/{row.get('SO', 0)}K", axis=1
        )

        # Separate by league
        al_teams = [
            "NYY",
            "BOS",
            "TOR",
            "TB",
            "BAL",
            "CLE",
            "DET",
            "KC",
            "CWS",
            "MIN",
            "HOU",
            "LAA",
            "OAK",
            "SEA",
            "TEX",
        ]

        al_cy = df[df["Team"].isin(al_teams)].nlargest(10, "CY_Score")
        nl_cy = df[~df["Team"].isin(al_teams)].nlargest(10, "CY_Score")

        # Save predictions
        if not al_cy.empty:
            al_cy.to_csv(f"{output_path}/al_cy_young_predictions.csv", index=False)
        if not nl_cy.empty:
            nl_cy.to_csv(f"{output_path}/nl_cy_young_predictions.csv", index=False)

        return al_cy, nl_cy

    except Exception as e:
        print(f"Error calculating Cy Young predictions: {e}")
        return None, None


def calculate_rookie_of_the_year_predictions():
    """Calculate Rookie of the Year predictions based on current stats"""
    try:
        df = batting_stats(2025)

        # Attempt to identify rookies
        # pybaseball may have a 'Rookie' or 'is_rookie' column, otherwise fallback to service time or age
        rookie_col = None
        for col in ["Rookie", "is_rookie", "rookie"]:
            if col in df.columns:
                rookie_col = col
                break

        if rookie_col:
            rookies = df[df[rookie_col] == True]
        else:
            # Fallback: Use age <= 25 and AB < 200 as a rough proxy (not perfect)
            rookies = df[(df.get("AB", pd.Series([0]*len(df))) < 200) & (df.get("age", pd.Series([26]*len(df))) <= 25)]

        if rookies.empty:
            print("No rookies found for ROY prediction")
            return None, None

        # Filter by minimum at-bats if available
        if "AB" in rookies.columns:
            rookies = rookies[rookies["AB"] >= 30]  # Lower threshold for rookies

        # Core stats for ROY scoring
        roy_score = 0
        roy_score += rookies.get("HR", 0) * 0.18
        roy_score += rookies.get("RBI", 0) * 0.13
        roy_score += rookies.get("AVG", 0) * 100 * 0.10
        roy_score += rookies.get("SB", 0) * 0.08
        if "wRC+" in rookies.columns:
            roy_score += rookies["wRC+"] * 0.22
        elif "OPS" in rookies.columns:
            roy_score += rookies["OPS"] * 50 * 0.22
        if "wOBA" in rookies.columns:
            roy_score += rookies["wOBA"] * 50 * 0.15

        rookies["ROY_Score"] = roy_score

        # Probability calculation
        if rookies["ROY_Score"].max() > 0:
            rookies["ROY_Probability"] = (
                rookies["ROY_Score"] / rookies["ROY_Score"].max() * 100
            ).round(1)
        else:
            rookies["ROY_Probability"] = 0

        # Key stats for display
        rookies["Key_Stats"] = rookies.apply(
            lambda row: f"{row.get('HR',0)}HR/{row.get('RBI',0)}RBI/{row.get('AVG',0):.3f}AVG", axis=1
        )

        # Separate by league
        al_teams = [
            "NYY", "BOS", "TOR", "TB", "BAL", "CLE", "DET", "KC", "CWS", "MIN",
            "HOU", "LAA", "OAK", "SEA", "TEX"
        ]
        al_roy = rookies[rookies["Team"].isin(al_teams)].nlargest(10, "ROY_Score")
        nl_roy = rookies[~rookies["Team"].isin(al_teams)].nlargest(10, "ROY_Score")

        # Save predictions
        if not al_roy.empty:
            al_roy.to_csv(f"{output_path}/al_roy_predictions.csv", index=False)
        if not nl_roy.empty:
            nl_roy.to_csv(f"{output_path}/nl_roy_predictions.csv", index=False)

        return al_roy, nl_roy

    except Exception as e:
        print(f"Error calculating Rookie of the Year predictions: {e}")
        return None, None


if __name__ == "__main__":
    try:
        # Calculate predictions
        al_mvp, nl_mvp = calculate_mvp_predictions()
        al_cy, nl_cy = calculate_cy_young_predictions()
        al_roy, nl_roy = calculate_rookie_of_the_year_predictions()

        # Create summary JSON
        summary = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "al_mvp": (
                al_mvp.to_dict("records")
                if al_mvp is not None and not al_mvp.empty
                else []
            ),
            "nl_mvp": (
                nl_mvp.to_dict("records")
                if nl_mvp is not None and not nl_mvp.empty
                else []
            ),
            "al_cy_young": (
                al_cy.to_dict("records")
                if al_cy is not None and not al_cy.empty
                else []
            ),
            "nl_cy_young": (
                nl_cy.to_dict("records")
                if nl_cy is not None and not nl_cy.empty
                else []
            ),
            "al_roy": (
                al_roy.to_dict("records")
                if al_roy is not None and not al_roy.empty
                else []
            ),
            "nl_roy": (
                nl_roy.to_dict("records")
                if nl_roy is not None and not nl_roy.empty
                else []
            ),
            "al_mvp_leader": (
                al_mvp.iloc[0]["Name"]
                if al_mvp is not None and not al_mvp.empty
                else "N/A"
            ),
            "nl_mvp_leader": (
                nl_mvp.iloc[0]["Name"]
                if nl_mvp is not None and not nl_mvp.empty
                else "N/A"
            ),
            "al_cy_leader": (
                al_cy.iloc[0]["Name"]
                if al_cy is not None and not al_cy.empty
                else "N/A"
            ),
            "nl_cy_leader": (
                nl_cy.iloc[0]["Name"]
                if nl_cy is not None and not nl_cy.empty
                else "N/A"
            ),
            "al_roy_leader": (
                al_roy.iloc[0]["Name"]
                if al_roy is not None and not al_roy.empty
                else "N/A"
            ),
            "nl_roy_leader": (
                nl_roy.iloc[0]["Name"]
                if nl_roy is not None and not nl_roy.empty
                else "N/A"
            ),
        }

        with open(f"{output_path}/award_predictions.json", "w") as f:
            json.dump(summary, f, indent=2)

        print("✓ MVP, Cy Young, and Rookie of the Year predictions calculated successfully!")

    except Exception as e:
        print(f"Critical error in mvp_cy_young_calculator.py: {e}")
        # Create minimal fallback
        fallback_summary = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e),
            "al_mvp": [],
            "nl_mvp": [],
            "al_cy_young": [],
            "nl_cy_young": [],
            "al_roy": [],
            "nl_roy": [],
            "al_mvp_leader": "Error",
            "nl_mvp_leader": "Error",
            "al_cy_leader": "Error",
            "nl_cy_leader": "Error",
            "al_roy_leader": "Error",
            "nl_roy_leader": "Error",
        }

        with open(f"{output_path}/award_predictions.json", "w") as f:
            json.dump(fallback_summary, f, indent=2)

        raise
