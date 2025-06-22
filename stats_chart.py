import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import pitching_stats

# Load 2025 stats
stats_2025 = pitching_stats(2025)

# Filter to qualified pitchers (e.g., IP >= 50)
qualified = stats_2025[stats_2025['IP'] >= 50].copy()

# Calculate WHIP manually
qualified['WHIP'] = (qualified['BB'] + qualified['H']) / qualified['IP']

# Set consistent style
sns.set(style="whitegrid")

# --- WHIP Chart ---
top_whip = qualified.sort_values('WHIP').head(10)
plt.figure(figsize=(12, 6))
sns.barplot(data=top_whip, x='WHIP', y='Name', palette='viridis')
plt.title('Top 10 WHIP Leaders – MLB 2025')
plt.xlabel('WHIP')
plt.ylabel('Pitcher')
plt.tight_layout()
plt.savefig("docs/whip_chart.png")
plt.close()

# --- ERA Chart ---
top_era = qualified.sort_values('ERA').head(10)
plt.figure(figsize=(12, 6))
sns.barplot(data=top_era, x='ERA', y='Name', palette='rocket')
plt.title('Top 10 ERA Leaders – MLB 2025')
plt.xlabel('ERA')
plt.ylabel('Pitcher')
plt.tight_layout()
plt.savefig("docs/era_chart.png")
plt.close()

# --- Strikeouts Chart ---
top_ks = qualified.sort_values('SO', ascending=False).head(10)
plt.figure(figsize=(12, 6))
sns.barplot(data=top_ks, x='SO', y='Name', palette='mako')
plt.title('Top 10 Strikeout Leaders – MLB 2025')
plt.xlabel('Strikeouts')
plt.ylabel('Pitcher')
plt.tight_layout()
plt.savefig("docs/strikeout_chart.png")
plt.close()
