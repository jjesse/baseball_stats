import pandas as pd
import json
import os
from datetime import datetime
from pybaseball import batting_stats, pitching_stats

# Ensure output directory exists
output_path = os.environ.get('OUTPUT_PATH', 'docs')
os.makedirs(output_path, exist_ok=True)

def calculate_mvp_predictions():
    """Calculate MVP predictions based on current stats"""
    try:
        df = batting_stats(2025)
        
        # Enhanced MVP scoring with more factors
        df['MVP_Score'] = (
            df['wRC+'] * 0.25 +
            df['HR'] * 0.2 +
            df['RBI'] * 0.15 +
            df['AVG'] * 100 * 0.1 +
            df['SB'] * 0.1 +
            df['OPS'] * 50 * 0.2
        )
        
        # Add probability calculation (simplified)
        df['MVP_Probability'] = (df['MVP_Score'] / df['MVP_Score'].max() * 100).round(1)
        
        # Separate by league
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
        
        # Enhanced Cy Young scoring
        df['CY_Score'] = (
            (5.0 - df['ERA']) * 25 +
            (2.0 - df['WHIP']) * 35 +
            df['SO'] * 0.15 +
            df['W'] * 8 +
            (5.0 - df['FIP']) * 20
        )
        
        # Add probability calculation
        df['CY_Probability'] = (df['CY_Score'] / df['CY_Score'].max() * 100).round(1)
        
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
    "nl_cy_leader": nl_cy.iloc[0]['Name'] if nl_cy is not None and not nl_cy.empty else "N/A"
}

with open(f"{output_path}/award_predictions.json", "w") as f:
    json.dump(summary, f, indent=2)

# Auto-trigger prediction tracking
try:
    from prediction_tracker import save_daily_predictions
    save_daily_predictions()
    print("✓ Daily predictions saved to tracking system")
except Exception as e:
    print(f"Warning: Could not save to tracking system: {e}")

print("MVP and Cy Young predictions calculated successfully!")