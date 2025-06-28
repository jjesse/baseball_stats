import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from pybaseball import standings

# Make sure output folder exists
os.makedirs("docs", exist_ok=True)

# Get list of standings DataFrames
division_standings = standings()

division_names = [
    "AL_East",
    "AL_Central",
    "AL_West",
    "NL_East",
    "NL_Central",
    "NL_West"
]

# Save each division CSV and HTML table
all_dfs = []

for df, name in zip(division_standings, division_names):
    csv_path = f"docs/standings_{name}.csv"
    html_path = f"docs/standings_{name}.html"
    
    df.to_csv(csv_path, index=False)
    df.to_html(html_path, index=False, classes='standings-table')
    
    all_dfs.append(df.assign(Division=name))  # For combining later

# Combine all into a master CSV
combined = pd.concat(all_dfs)
combined.to_csv("docs/standings_all.csv", index=False)

# Create bar chart of total wins per team
plt.figure(figsize=(12, 6))
plt.bar(combined["Tm"], combined["W"], color="steelblue")
plt.xticks(rotation=90)
plt.title("Total Wins by Team")
plt.xlabel("Team")
plt.ylabel("Wins")
plt.tight_layout()
plt.savefig("docs/standings_wins_chart.png")
plt.close()

# Save last updated timestamp
with open("docs/last_updated_standings.txt", "w") as f:
    f.write(datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S"))

print("Standings data and charts successfully generated.")
# This script generates standings data and charts for MLB divisions using the pybaseball library.
# It saves individual division standings as CSV and HTML files, combines them into a master CSV,
# and creates a bar chart of total wins by team. The last updated timestamp is also saved
# to track when the data was last refreshed.
# The output files are saved in the "docs" directory.
# Make sure to have the pybaseball library installed and up-to-date to fetch the latest standings data.
# You can install it using pip:
# pip install pybaseball 