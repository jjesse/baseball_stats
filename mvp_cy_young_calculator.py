import pandas as pd
import json
import os
from datetime import datetime
from pybaseball import batting_stats, pitching_stats

# Ensure output directory exists
output_path = os.environ.get('OUTPUT_PATH', 'docs')
os.makedirs(output_path, exist_ok=True)

# This is a simplified MVP/Cy Young calculator
# In a real implementation, you'd use more sophisticated algorithms

def calculate_mvp_predictions():
    """Calculate MVP predictions based on current stats"""
    try:
        df = batting_stats(2025)
        
        # Simple MVP scoring based on key stats
        df['MVP_Score'] = (
            df['wRC+'] * 0.3 +
            df['HR'] * 0.2 +
            df['RBI'] * 0.2 +
            df['AVG'] * 100 * 0.15 +
            df['SB'] * 0.15
        )
        
        # Separate by league (simplified)
        al_teams = ['NYY', 'BOS', 'TOR', 'TB', 'BAL', 'CLE', 'DET', 'KC', 'CWS', 'MIN', 'HOU', 'LAA', 'OAK', 'SEA', 'TEX']
        
        al_mvp = df[df['Team'].isin(al_teams)].nlargest(10, 'MVP_Score')
        nl_mvp = df[~df['Team'].isin(al_teams)].nlargest(10, 'MVP_Score')
        
        # Save predictions
        al_mvp.to_csv(f"{output_path}/al_mvp_predictions.csv", index=False)
        nl_mvp.to_csv(f"{output_path}/nl_mvp_predictions.csv", index=False)
        
        return al_mvp, nl_mvp
        
    except Exception as e:
        print(f"Error calculating MVP predictions: {e}")
        return None, None

def calculate_cy_young_predictions():
    """Calculate Cy Young predictions based on current stats"""
    try:
        df = pitching_stats(2025)
        
        # Simple Cy Young scoring
        df['CY_Score'] = (
            (5.0 - df['ERA']) * 20 +
            (2.0 - df['WHIP']) * 30 +
            df['SO'] * 0.1 +
            df['W'] * 5 +
            (5.0 - df['FIP']) * 15
        )
        
        # Separate by league
        al_teams = ['NYY', 'BOS', 'TOR', 'TB', 'BAL', 'CLE', 'DET', 'KC', 'CWS', 'MIN', 'HOU', 'LAA', 'OAK', 'SEA', 'TEX']
        
        al_cy = df[df['Team'].isin(al_teams)].nlargest(10, 'CY_Score')
        nl_cy = df[~df['Team'].isin(al_teams)].nlargest(10, 'CY_Score')
        
        # Save predictions
        al_cy.to_csv(f"{output_path}/al_cy_young_predictions.csv", index=False)
        nl_cy.to_csv(f"{output_path}/nl_cy_young_predictions.csv", index=False)
        
        return al_cy, nl_cy
        
    except Exception as e:
        print(f"Error calculating Cy Young predictions: {e}")
        return None, None

# Calculate predictions
al_mvp, nl_mvp = calculate_mvp_predictions()
al_cy, nl_cy = calculate_cy_young_predictions()

# Create summary JSON
summary = {
    "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "al_mvp_leader": al_mvp.iloc[0]['Name'] if al_mvp is not None and not al_mvp.empty else "N/A",
    "nl_mvp_leader": nl_mvp.iloc[0]['Name'] if nl_mvp is not None and not nl_mvp.empty else "N/A",
    "al_cy_leader": al_cy.iloc[0]['Name'] if al_cy is not None and not al_cy.empty else "N/A",
    "nl_cy_leader": nl_cy.iloc[0]['Name'] if nl_cy is not None and not al_cy.empty else "N/A"
}

with open(f"{output_path}/award_predictions.json", "w") as f:
    json.dump(summary, f, indent=2)

print("MVP and Cy Young predictions calculated successfully!")