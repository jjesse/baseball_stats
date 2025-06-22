import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import pitching_stats

# Load 2025 stats
stats_2025 = pitching_stats(2025)
stats_2025['WHIP_Calc'] = (stats_2025['BB'] + stats_2025['H']) / stats_2025['IP']
qualified = stats_2025[stats_2025['IP'] >= 50].copy()
top_whip = qualified.sort_values('WHIP_Calc').head(10)

sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))
sns.barplot(data=top_whip, x='WHIP_Calc', y='Name', palette='viridis')
plt.xlabel('WHIP')
plt.ylabel('Pitcher')
plt.title('Top 10 WHIP Leaders – MLB 2025 (min 50 IP)')
plt.xlim(0.5, top_whip['WHIP_Calc'].max() + 0.1)
plt.tight_layout()

# Save chart
plt.savefig("whip_chart.png")
