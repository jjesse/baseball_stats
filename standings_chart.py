import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from pybaseball import standings

# Make sure output folder exists
os.makedirs("docs", exist_ok=True)

try:
    # Get list of standings DataFrames
    division_standings = standings()
    print(f"DEBUG: standings() returned {len(division_standings) if division_standings else 0} DataFrames")
except Exception as e:
    print(f"Error fetching standings: {e}")
    # Create a fallback message file
    with open("docs/last_updated_standings.txt", "w") as f:
        f.write(f"Error: Unable to fetch standings data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit(1)

# Validate the data
if not division_standings or len(division_standings) == 0:
    print("Error: standings() returned empty or None.")
    with open("docs/last_updated_standings.txt", "w") as f:
        f.write(f"Error: No standings data available - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit(1)

if len(division_standings) != 6:
    print(f"Warning: Expected 6 divisions, got {len(division_standings)}. Proceeding with available data.")

division_names = [
    "al_east",
    "al_central", 
    "al_west",
    "nl_east",
    "nl_central",
    "nl_west"
]

all_dfs = []
processed_divisions = 0

for i, df in enumerate(division_standings):
    if i >= len(division_names):
        print(f"Warning: More divisions ({i+1}) than expected names ({len(division_names)})")
        break
        
    name = division_names[i]
    print(f"DEBUG: Processing {name}, shape: {df.shape if not df.empty else 'EMPTY'}")
    
    if df.empty:
        print(f"Warning: Division {name} is empty. Skipping.")
        continue
    
    # Ensure required columns exist
    if 'Tm' not in df.columns or 'W' not in df.columns:
        print(f"Warning: Division {name} missing required columns. Available: {list(df.columns)}")
        continue
    
    try:
        # Save individual division files
        csv_path = f"docs/standings_{name}.csv"
        html_path = f"docs/standings_{name}.html"
        
        df.to_csv(csv_path, index=False)
        df.to_html(html_path, index=False, classes='standings-table')
        
        # Add to master list
        df_copy = df.copy()
        df_copy['Division'] = name
        all_dfs.append(df_copy)
        processed_divisions += 1
        
        print(f"Successfully processed {name}")
        
    except Exception as e:
        print(f"Error processing {name}: {e}")
        continue

print(f"Processed {processed_divisions} divisions successfully")

# Check if we have any data to work with
if not all_dfs:
    print("Error: No division standings were successfully processed.")
    with open("docs/last_updated_standings.txt", "w") as f:
        f.write(f"Error: No valid standings data processed - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit(1)

# Combine all into a master CSV
try:
    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv("docs/standings_all.csv", index=False)
    print(f"Created combined standings with {len(combined)} teams")
except Exception as e:
    print(f"Error creating combined standings: {e}")
    # Still continue to create timestamp file

# Create wins chart if we have the required columns
try:
    if 'Tm' in combined.columns and 'W' in combined.columns:
        plt.figure(figsize=(12, 6))
        plt.bar(combined["Tm"], combined["W"], color="steelblue")
        plt.xticks(rotation=90)
        plt.title("Total Wins by Team")
        plt.xlabel("Team")
        plt.ylabel("Wins")
        plt.tight_layout()
        plt.savefig("docs/standings_wins_chart.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("Created wins chart")
    else:
        print("Warning: Cannot create wins chart - missing required columns")
except Exception as e:
    print(f"Error creating wins chart: {e}")

# Save last updated timestamp
try:
    with open("docs/last_updated_standings.txt", "w") as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Updated timestamp file")
except Exception as e:
    print(f"Error updating timestamp: {e}")

print("Standings processing completed.")


# This script generates standings data and charts for MLB divisions using the pybaseball library.
# It saves individual division standings as CSV and HTML files, combines them into a master CSV,
# and creates a bar chart of total wins by team. The last updated timestamp is also saved
# to track when the data was last refreshed.
# The output files are saved in the "docs" directory.
# Make sure to have the pybaseball library installed and up-to-date to fetch the latest standings data.
# You can install it using pip:
# pip install pybaseball