import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime

# Set style and ensure output directory
sns.set_style("whitegrid")
os.makedirs("docs", exist_ok=True)

def create_award_charts():
    """Create visual charts for MVP and Cy Young races"""
    
    try:
        # Load the predictions data
        with open('docs/award_predictions.json', 'r') as f:
            data = json.load(f)
        
        # Create charts for each award race
        awards = [
            ('al_mvp', 'American League MVP Race', 'Blues'),
            ('nl_mvp', 'National League MVP Race', 'Reds'), 
            ('al_cy_young', 'American League Cy Young Race', 'Greens'),
            ('nl_cy_young', 'National League Cy Young Race', 'Purples')
        ]
        
        for award_key, title, color_palette in awards:
            if award_key not in data:
                continue
                
            # Get top 8 candidates for the chart
            candidates = data[award_key][:8]
            
            if not candidates:
                continue
                
            # Create DataFrame
            df = pd.DataFrame(candidates)
            
            # Determine probability field
            prob_field = 'MVP_Probability' if 'mvp' in award_key else 'CyYoung_Probability'
            
            # Create horizontal bar chart
            plt.figure(figsize=(12, 8))
            
            # Create the plot
            bars = plt.barh(range(len(df)), df[prob_field], 
                           color=sns.color_palette(color_palette, len(df)))
            
            # Customize the chart
            plt.xlabel('Probability (%)', fontsize=12, fontweight='bold')
            plt.ylabel('Players', fontsize=12, fontweight='bold')
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            
            # Set y-axis labels (player names and teams)
            labels = [f"{row['Name']}\n({row['Team']})" for _, row in df.iterrows()]
            plt.yticks(range(len(df)), labels)
            
            # Add percentage labels on bars
            for i, (bar, prob) in enumerate(zip(bars, df[prob_field])):
                plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                        f'{prob}%', ha='left', va='center', fontweight='bold')
            
            # Invert y-axis so highest probability is at top
            plt.gca().invert_yaxis()
            
            # Set x-axis limit
            plt.xlim(0, max(df[prob_field]) * 1.15)
            
            # Add grid
            plt.grid(axis='x', alpha=0.3)
            
            # Tight layout and save
            plt.tight_layout()
            chart_filename = f"docs/{award_key}_race_chart.png"
            plt.savefig(chart_filename, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Created {title} chart: {chart_filename}")
        
        # Create summary race chart showing leaders from each league/award
        create_summary_chart(data)
        
        print("🏆 Award race charts generated successfully!")
        
    except Exception as e:
        print(f"Error creating award charts: {e}")
        
def create_summary_chart(data):
    """Create a summary chart showing the leader from each award race"""
    
    try:
        leaders = []
        
        # Get the leader from each race
        races = [
            ('al_mvp', 'AL MVP', 'MVP_Probability'),
            ('nl_mvp', 'NL MVP', 'MVP_Probability'),
            ('al_cy_young', 'AL Cy Young', 'CyYoung_Probability'),
            ('nl_cy_young', 'NL Cy Young', 'CyYoung_Probability')
        ]
        
        for race_key, race_name, prob_field in races:
            if race_key in data and data[race_key]:
                leader = data[race_key][0]
                leaders.append({
                    'Award': race_name,
                    'Player': f"{leader['Name']} ({leader['Team']})",
                    'Probability': leader[prob_field],
                    'Stats': leader['Key_Stats']
                })
        
        if not leaders:
            return
            
        # Create summary chart
        plt.figure(figsize=(14, 8))
        
        df = pd.DataFrame(leaders)
        
        # Create grouped bar chart
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
        bars = plt.bar(range(len(df)), df['Probability'], color=colors)
        
        # Customize
        plt.xlabel('Award Categories', fontsize=12, fontweight='bold')
        plt.ylabel('Win Probability (%)', fontsize=12, fontweight='bold')
        plt.title('2025 MLB Award Race Leaders', fontsize=16, fontweight='bold', pad=20)
        
        # Set x-axis labels
        plt.xticks(range(len(df)), df['Award'], fontsize=10)
        
        # Add percentage labels on bars
        for bar, prob, player, stats in zip(bars, df['Probability'], df['Player'], df['Stats']):
            # Probability on top of bar
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{prob}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            # Player name below x-axis
            plt.text(bar.get_x() + bar.get_width()/2, -8, 
                    player, ha='center', va='top', fontweight='bold', fontsize=9)
            
            # Stats below player name
            plt.text(bar.get_x() + bar.get_width()/2, -15, 
                    stats, ha='center', va='top', fontsize=8, style='italic')
        
        # Set y-axis limit
        plt.ylim(-25, max(df['Probability']) * 1.15)
        
        # Add grid
        plt.grid(axis='y', alpha=0.3)
        
        # Remove x-axis labels since we're adding custom ones
        plt.tick_params(axis='x', bottom=False)
        
        # Tight layout and save
        plt.tight_layout()
        plt.savefig("docs/award_leaders_summary.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✅ Created award leaders summary chart")
        
    except Exception as e:
        print(f"Error creating summary chart: {e}")

if __name__ == "__main__":
    create_award_charts()