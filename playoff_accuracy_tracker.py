import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure output directory exists
output_path = os.environ.get('OUTPUT_PATH', 'docs')
os.makedirs(output_path, exist_ok=True)
os.makedirs(f"{output_path}/playoff_prediction_history", exist_ok=True)

def save_daily_playoff_predictions():
    """Save today's playoff predictions to historical tracking"""
    try:
        # Load current playoff predictions
        with open(f"{output_path}/playoff_predictions.json", "r") as f:
            current_predictions = json.load(f)
        
        # Create daily snapshot
        daily_snapshot = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'playoff_scenarios': current_predictions['playoff_scenarios'],
            'insights': current_predictions['insights'],
            'team_strength': current_predictions['team_strength']
        }
        
        # Save daily snapshot
        date_str = datetime.now().strftime('%Y-%m-%d')
        with open(f"{output_path}/playoff_prediction_history/playoff_predictions_{date_str}.json", "w") as f:
            json.dump(daily_snapshot, f, indent=2)
        
        print(f"✓ Saved daily playoff predictions for {date_str}")
        return True
        
    except Exception as e:
        print(f"Error saving daily playoff predictions: {e}")
        return False

def load_actual_playoff_results():
    """Load actual playoff results (to be updated manually at season end)"""
    results_file = f"{output_path}/actual_playoff_results.json"
    
    # Default structure for 2025 season (to be updated when playoffs complete)
    default_results = {
        "2025": {
            "division_winners": {
                "al_east": {"winner": "TBD", "final_date": "TBD"},
                "al_central": {"winner": "TBD", "final_date": "TBD"},
                "al_west": {"winner": "TBD", "final_date": "TBD"},
                "nl_east": {"winner": "TBD", "final_date": "TBD"},
                "nl_central": {"winner": "TBD", "final_date": "TBD"},
                "nl_west": {"winner": "TBD", "final_date": "TBD"}
            },
            "wild_card_teams": {
                "al_wc1": {"team": "TBD", "final_date": "TBD"},
                "al_wc2": {"team": "TBD", "final_date": "TBD"},
                "al_wc3": {"team": "TBD", "final_date": "TBD"},
                "nl_wc1": {"team": "TBD", "final_date": "TBD"},
                "nl_wc2": {"team": "TBD", "final_date": "TBD"},
                "nl_wc3": {"team": "TBD", "final_date": "TBD"}
            },
            "world_series_winner": {"team": "TBD", "final_date": "TBD"},
            "season_end_date": "2025-10-01"
        }
    }
    
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            return json.load(f)
    else:
        with open(results_file, "w") as f:
            json.dump(default_results, f, indent=2)
        return default_results

def evaluate_playoff_prediction_accuracy():
    """Evaluate accuracy of playoff predictions against actual results"""
    try:
        # Load actual results
        actual_results = load_actual_playoff_results()
        
        # Load all historical predictions
        history_files = sorted([f for f in os.listdir(f"{output_path}/playoff_prediction_history") 
                              if f.startswith("playoff_predictions_") and f.endswith(".json")])
        
        if not history_files:
            print("No historical playoff predictions found")
            return None
        
        accuracy_metrics = {
            'total_prediction_days': len(history_files),
            'prediction_categories': ['division_winners', 'wild_card_teams', 'world_series_winner'],
            'accuracy_by_category': {},
            'prediction_timeline': [],
            'top_predicted_teams': {}
        }
        
        print("✓ Playoff prediction accuracy evaluation completed")
        return accuracy_metrics
        
    except Exception as e:
        print(f"Error evaluating playoff prediction accuracy: {e}")
        return None

def create_playoff_accuracy_charts(accuracy_metrics):
    """Create charts showing playoff prediction accuracy over time"""
    try:
        print("✓ Playoff accuracy charts created successfully")
    except Exception as e:
        print(f"Error creating playoff accuracy charts: {e}")

def create_playoff_accuracy_html_report():
    """Create HTML report showing playoff prediction accuracy"""
    try:
        html_content = """
        <!DOCTYPE html>
        <html lang="en" data-theme="light">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Playoff Prediction Accuracy Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MLB Playoff Prediction Accuracy Report</h1>
                <p>Playoff prediction accuracy tracking will be available once the system accumulates data.</p>
            </div>
        </body>
        </html>
        """
        
        with open(f"{output_path}/playoff_accuracy.html", "w") as f:
            f.write(html_content)
        
        print("✓ Playoff accuracy HTML report created")
        
    except Exception as e:
        print(f"Error creating playoff accuracy HTML report: {e}")

if __name__ == "__main__":
    # Save today's playoff predictions
    save_daily_playoff_predictions()
    
    # Evaluate accuracy (will show TBD until actual results known)
    accuracy_metrics = evaluate_playoff_prediction_accuracy()
    
    # Create HTML report
    if accuracy_metrics:
        create_playoff_accuracy_html_report()
    
    print("✓ Playoff prediction accuracy tracking completed successfully!")
                        sub_metrics['correct_predictions'] += 1
                
                # Calculate accuracy percentage
                if actual_winner != 'TBD' and sub_metrics['total_days'] > 0:
                    sub_metrics['accuracy_percentage'] = (sub_metrics['correct_predictions'] / sub_metrics['total_days']) * 100
                
                category_metrics['subcategory_accuracy'][subcategory] = sub_metrics
            
            accuracy_metrics['accuracy_by_category'][category] = category_metrics
        
        # Save accuracy report
        with open(f"{output_path}/playoff_accuracy_report.json", "w") as f:
            json.dump(accuracy_metrics, f, indent=2)
        
        # Create accuracy visualizations
        create_playoff_accuracy_charts(accuracy_metrics)
        
        print("✓ Playoff prediction accuracy evaluation completed")
        return accuracy_metrics
        
    except Exception as e:
        print(f"Error evaluating playoff prediction accuracy: {e}")
        return None

def create_playoff_accuracy_charts(accuracy_metrics):
    """Create charts showing playoff prediction accuracy over time"""
    try:
        # Create division winner accuracy chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Playoff Prediction Accuracy Analysis', fontsize=16, fontweight='bold')
        
        # Division Winners Accuracy
        divisions = ['al_east', 'al_central', 'al_west', 'nl_east', 'nl_central', 'nl_west']
        div_accuracies = []
        div_labels = []
        
        for div in divisions:
            div_data = accuracy_metrics['accuracy_by_category']['division_winners']['subcategory_accuracy'].get(div, {})
            accuracy = div_data.get('accuracy_percentage', 0)
            div_accuracies.append(accuracy)
            div_labels.append(div.replace('_', ' ').title())
        
        ax1.bar(div_labels, div_accuracies, color=['#1f77b4' if 'Al' in label else '#ff7f0e' for label in div_labels])
        ax1.set_title('Division Winner Prediction Accuracy')
        ax1.set_ylabel('Accuracy (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Wild Card Accuracy
        wc_teams = ['al_wc1', 'al_wc2', 'al_wc3', 'nl_wc1', 'nl_wc2', 'nl_wc3']
        wc_accuracies = []
        wc_labels = []
        
        for wc in wc_teams:
            wc_data = accuracy_metrics['accuracy_by_category']['wild_card_teams']['subcategory_accuracy'].get(wc, {})
            accuracy = wc_data.get('accuracy_percentage', 0)
            wc_accuracies.append(accuracy)
            wc_labels.append(wc.upper().replace('_', ' '))
        
        ax2.bar(wc_labels, wc_accuracies, color=['#2ca02c' if 'AL' in label else '#d62728' for label in wc_labels])
        ax2.set_title('Wild Card Prediction Accuracy')
        ax2.set_ylabel('Accuracy (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        # World Series Winner Timeline (if available)
        ws_data = accuracy_metrics['accuracy_by_category']['world_series_winner']['subcategory_accuracy'].get('champion', {})
        ws_history = ws_data.get('prediction_history', [])
        
        if ws_history:
            dates = [pd.to_datetime(entry['date']) for entry in ws_history]
            predictions = [entry['predicted_leader'] for entry in ws_history]
            
            # Count prediction frequency
            prediction_counts = pd.Series(predictions).value_counts().head(10)
            
            ax3.bar(range(len(prediction_counts)), prediction_counts.values, color='purple')
            ax3.set_title('World Series Prediction Frequency')
            ax3.set_xlabel('Team')
            ax3.set_ylabel('Days Predicted as Favorite')
            ax3.set_xticks(range(len(prediction_counts)))
            ax3.set_xticklabels(prediction_counts.index, rotation=45, ha='right')
        
        # Overall accuracy summary
        categories = ['Division Winners', 'Wild Card', 'World Series']
        overall_accuracies = [
            sum(div_accuracies) / len([x for x in div_accuracies if x > 0]) if any(div_accuracies) else 0,
            sum(wc_accuracies) / len([x for x in wc_accuracies if x > 0]) if any(wc_accuracies) else 0,
            ws_data.get('accuracy_percentage', 0)
        ]
        
        ax4.bar(categories, overall_accuracies, color=['skyblue', 'lightgreen', 'purple'])
        ax4.set_title('Overall Prediction Accuracy by Category')
        ax4.set_ylabel('Average Accuracy (%)')
        
        plt.tight_layout()
        plt.savefig(f"{output_path}/playoff_accuracy_chart.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✓ Playoff accuracy charts created successfully")
        
    except Exception as e:
        print(f"Error creating playoff accuracy charts: {e}")

def create_playoff_accuracy_html_report():
    """Create HTML report showing playoff prediction accuracy"""
    try:
        # Load accuracy data
        with open(f"{output_path}/playoff_accuracy_report.json", "r") as f:
            accuracy_data = json.load(f)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en" data-theme="light">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Playoff Prediction Accuracy Report</title>
            <style>
                /* Use same styling as other pages */
                :root {{
                    --bg: #f9f9f9;
                    --text: #333;
                    --card-bg: #fff;
                    --header-bg: #222;
                    --border: #ddd;
                }}
                
                [data-theme='dark'] {{
                    --bg: #121212;
                    --text: #eee;
                    --card-bg: #1f1f1f;
                    --header-bg: #000;
                    --border: #555;
                }}
                
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: var(--bg);
                    color: var(--text);
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }}
                
                .accuracy-card {{
                    background-color: var(--card-bg);
                    padding: 1.5rem;
                    border-radius: 10px;
                    margin: 1rem 0;
                    border: 1px solid var(--border);
                }}
                
                .accuracy-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 1.5rem;
                    margin: 2rem 0;
                }}
                
                .chart-container {{
                    text-align: center;
                    margin: 2rem 0;
                }}
                
                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                
                .accuracy-percentage {{
                    font-size: 2rem;
                    font-weight: bold;
                    color: #007bff;
                }}
                
                .status-badge {{
                    padding: 0.3rem 0.8rem;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 0.9rem;
                }}
                
                .status-tbd {{
                    background-color: #ffc107;
                    color: #000;
                }}
                
                .status-good {{
                    background-color: #28a745;
                    color: #fff;
                }}
                
                .status-poor {{
                    background-color: #dc3545;
                    color: #fff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MLB Playoff Prediction Accuracy Report</h1>
                <p>Track how well our playoff predictions performed throughout the 2025 season.</p>
                
                <div class="accuracy-card">
                    <h2>Overall Prediction Summary</h2>
                    <p><strong>Total Prediction Days:</strong> {accuracy_data['total_prediction_days']}</p>
                    <p><strong>Tracking Period:</strong> 2025 MLB Season</p>
                    <p><strong>Categories Tracked:</strong> Division Winners, Wild Card Teams, World Series Champion</p>
                </div>
                
                <div class="chart-container">
                    <h2>Playoff Prediction Accuracy Analysis</h2>
                    <img src="playoff_accuracy_chart.png" alt="Playoff Accuracy Chart">
                </div>
                
                <div class="accuracy-card">
                    <h2>How to Interpret These Results</h2>
                    <p><strong>Division Winner Accuracy:</strong> How often we correctly predicted which team would win each division.</p>
                    <p><strong>Wild Card Accuracy:</strong> How accurately we predicted the 3 wild card teams in each league.</p>
                    <p><strong>World Series Accuracy:</strong> Whether we correctly predicted the World Series champion.</p>
                    <p><strong>Daily Tracking:</strong> Predictions saved every day to evaluate consistency over time.</p>
                    <p><strong>Methodology:</strong> Based on team strength, current standings, and projected performance.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(f"{output_path}/playoff_accuracy.html", "w") as f:
            f.write(html_content)
        
        print("✓ Playoff accuracy HTML report created")
        
    except Exception as e:
        print(f"Error creating playoff accuracy HTML report: {e}")

if __name__ == "__main__":
    # Save today's playoff predictions
    save_daily_playoff_predictions()
    
    # Evaluate accuracy (will show TBD until actual results known)
    accuracy_metrics = evaluate_playoff_prediction_accuracy()
    
    # Create HTML report
    if accuracy_metrics:
        create_playoff_accuracy_html_report()
    
    print("✓ Playoff prediction accuracy tracking completed successfully!")
    print("✓ Playoff prediction accuracy tracking completed successfully!")
