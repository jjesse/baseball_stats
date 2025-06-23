import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import pitching_stats

# Load 2025 MLB pitching stats
stats_2025 = pitching_stats(2025)

# Filter: Only pitchers with >= 50 IP
qualified = stats_2025[stats_2025['IP'] >= 50].copy()

# Add calculated WHIP column (if not already present)
qualified['WHIP'] = (qualified['BB'] + qualified['H']) / qualified['IP']

# Apply consistent plot styling
sns.set(style="whitegrid")

# Generic chart generator
def make_chart(df, x_col, title, filename, ascending=True, palette='deep', xlabel=None):
    top = df.sort_values(x_col, ascending=ascending).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top, x=x_col, y='Name', hue='Name', palette=palette, legend=False)
    plt.title(title)
    plt.xlabel(xlabel or x_col)
    plt.ylabel("Pitcher")
    plt.tight_layout()
    plt.savefig(f"docs/{filename}")
    plt.close()

# CSV table export
def save_table(df, x_col, filename, ascending=True):
    top = df.sort_values(x_col, ascending=ascending).head(10)
    top[['Name', x_col]].to_csv(f"docs/{filename}", index=False)

# 1. WHIP
make_chart(qualified, 'WHIP', 'Top 10 WHIP Leaders – MLB 2025', 'whip_chart.png', ascending=True, palette='viridis')
save_table(qualified, 'WHIP', 'whip_table.csv', ascending=True)

# 2. ERA
make_chart(qualified, 'ERA', 'Top 10 ERA Leaders – MLB 2025', 'era_chart.png', ascending=True, palette='rocket')
save_table(qualified, 'ERA', 'era_table.csv', ascending=True)

# 3. Strikeouts (SO)
make_chart(qualified, 'SO', 'Top 10 Strikeout Leaders – MLB 2025', 'strikeout_chart.png', ascending=False, palette='mako', xlabel='Strikeouts')
save_table(qualified, 'SO', 'strikeout_table.csv', ascending=False)

# 4. Walks (BB)
make_chart(qualified, 'BB', 'Top 10 Most Walks – MLB 2025', 'bb_chart.png', ascending=False, palette='flare', xlabel='Walks')
save_table(qualified, 'BB', 'bb_table.csv', ascending=False)

# 5. K/BB ratio
make_chart(qualified, 'K/BB', 'Top 10 K/BB Ratio – MLB 2025', 'kbb_chart.png', ascending=False, palette='cubehelix')
save_table(qualified, 'K/BB', 'kbb_table.csv', ascending=False)

# 6. HR/9
make_chart(qualified, 'HR/9', 'Top 10 Lowest HR/9 – MLB 2025', 'hr9_chart.png', ascending=True, palette='crest', xlabel='HR per 9 innings')
save_table(qualified, 'HR/9', 'hr9_table.csv', ascending=True)

# 7. FIP
make_chart(qualified, 'FIP', 'Top 10 FIP Leaders – MLB 2025', 'fip_chart.png', ascending=True, palette='coolwarm')
save_table(qualified, 'FIP', 'fip_table.csv', ascending=True)
