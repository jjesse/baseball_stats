import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure output directory exists
output_path = os.environ.get('OUTPUT_PATH', 'docs')
os.makedirs(output_path, exist_ok=True)
os.makedirs(f"{output_path}/prediction_history", exist_ok=True)

def save_daily_predictions():
    """Save today's predictions to historical tracking"""
    try:
        # Load current predictions
        with open(f"{output_path}/award_predictions.json", "r") as f:
            current_predictions = json.load(f)
        
        # Load current prediction CSVs
        predictions_data = {}
        award_files = {
            'al_mvp': f"{output_path}/al_mvp_predictions.csv",
            'nl_mvp': f"{output_path}/nl_mvp_predictions.csv", 
            'al_cy': f"{output_path}/al_cy_young_predictions.csv",
            'nl_cy': f"{output_path}/nl_cy_young_predictions.csv"
        }
        
        for award, file_path in award_files.items():
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if not df.empty:
                    # Get top 10 predictions with probabilities
                    top_predictions = df.head(10).to_dict('records')
                    predictions_data[award] = top_predictions
        
        # Create daily snapshot
        daily_snapshot = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'leaders': current_predictions,
            'full_predictions': predictions_data
        }
        
        # Save daily snapshot
        date_str = datetime.now().strftime('%Y-%m-%d')
        with open(f"{output_path}/prediction_history/predictions_{date_str}.json", "w") as f:
            json.dump(daily_snapshot, f, indent=2)
        
        print(f"✓ Saved daily predictions for {date_str}")
        return True
        
    except Exception as e:
        print(f"Error saving daily predictions: {e}")
        return False

def load_actual_winners():
    """Load actual award winners (to be updated manually at season end)"""
    winners_file = f"{output_path}/actual_winners.json"
    
    # Default structure for 2025 season (to be updated when winners announced)
    default_winners = {
        "2025": {
            "al_mvp": {"winner": "TBD", "announced_date": "TBD"},
            "nl_mvp": {"winner": "TBD", "announced_date": "TBD"},
            "al_cy": {"winner": "TBD", "announced_date": "TBD"},
            "nl_cy": {"winner": "TBD", "announced_date": "TBD"}
        }
    }
    
    if os.path.exists(winners_file):
        with open(winners_file, "r") as f:
            return json.load(f)
    else:
        with open(winners_file, "w") as f:
            json.dump(default_winners, f, indent=2)
        return default_winners

def evaluate_prediction_accuracy():
    """Evaluate accuracy of predictions against actual winners"""
    try:
        # Load actual winners
        actual_winners = load_actual_winners()
        
        # Load all historical predictions
        history_files = sorted([f for f in os.listdir(f"{output_path}/prediction_history") 
                              if f.startswith("predictions_") and f.endswith(".json")])
        
        if not history_files:
            print("No historical predictions found")
            return None
        
        accuracy_metrics = {
            'total_predictions': len(history_files),
            'awards': ['al_mvp', 'nl_mvp', 'al_cy', 'nl_cy'],
            'accuracy_by_award': {},
            'prediction_timeline': [],
            'top_predicted_players': {}
        }
        
        # Analyze each award
        for award in accuracy_metrics['awards']:
            award_metrics = {
                'correct_predictions': 0,
                'total_days': 0,
                'accuracy_percentage': 0,
                'prediction_history': [],
                'final_accuracy': 'TBD'
            }
            
            # Check if we have actual winner for this award
            actual_winner = actual_winners.get('2025', {}).get(award, {}).get('winner', 'TBD')
            
            # Track predictions over time
            for history_file in history_files:
                with open(f"{output_path}/prediction_history/{history_file}", "r") as f:
                    daily_data = json.load(f)
                
                # Get the predicted leader for this award
                predicted_leader = daily_data.get('leaders', {}).get(f"{award}_leader", "N/A")
                
                award_metrics['prediction_history'].append({
                    'date': daily_data['date'],
                    'predicted_leader': predicted_leader,
                    'correct': predicted_leader == actual_winner if actual_winner != 'TBD' else None
                })
                
                award_metrics['total_days'] += 1
                if actual_winner != 'TBD' and predicted_leader == actual_winner:
                    award_metrics['correct_predictions'] += 1
            
            # Calculate accuracy percentage
            if actual_winner != 'TBD' and award_metrics['total_days'] > 0:
                award_metrics['accuracy_percentage'] = (award_metrics['correct_predictions'] / award_metrics['total_days']) * 100
                award_metrics['final_accuracy'] = 'Correct' if predicted_leader == actual_winner else 'Incorrect'
            
            accuracy_metrics['accuracy_by_award'][award] = award_metrics
        
        # Save accuracy report
        with open(f"{output_path}/prediction_accuracy_report.json", "w") as f:
            json.dump(accuracy_metrics, f, indent=2)
        
        # Create accuracy visualizations
        create_accuracy_charts(accuracy_metrics)
        
        print("✓ Prediction accuracy evaluation completed")
        return accuracy_metrics
        
    except Exception as e:
        print(f"Error evaluating prediction accuracy: {e}")
        return None

def create_accuracy_charts(accuracy_metrics):
    """Create charts showing prediction accuracy over time"""
    try:
        # Create accuracy timeline chart
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Award Prediction Accuracy Over Time', fontsize=16, fontweight='bold')
        
        award_titles = {
            'al_mvp': 'AL MVP',
            'nl_mvp': 'NL MVP', 
            'al_cy': 'AL Cy Young',
            'nl_cy': 'NL Cy Young'
        }
        
        for i, (award, metrics) in enumerate(accuracy_metrics['accuracy_by_award'].items()):
            ax = axes[i//2, i%2]
            
            # Extract dates and predictions
            dates = [pd.to_datetime(entry['date']) for entry in metrics['prediction_history']]
            predictions = [entry['predicted_leader'] for entry in metrics['prediction_history']]
            
            if dates and predictions:
                # Count prediction frequency
                prediction_counts = pd.Series(predictions).value_counts()
                
                # Plot top 5 most predicted players
                top_predictions = prediction_counts.head(5)
                ax.bar(range(len(top_predictions)), top_predictions.values, 
                       color=plt.cm.Set3(range(len(top_predictions))))
                ax.set_xticks(range(len(top_predictions)))
                ax.set_xticklabels(top_predictions.index, rotation=45, ha='right')
                ax.set_title(f"{award_titles[award]}\n({metrics['accuracy_percentage']:.1f}% accuracy)")
                ax.set_ylabel('Days as Leader')
        
        plt.tight_layout()
        plt.savefig(f"{output_path}/prediction_accuracy_chart.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        # Create prediction timeline chart
        plt.figure(figsize=(15, 10))
        
        for i, (award, metrics) in enumerate(accuracy_metrics['accuracy_by_award'].items()):
            dates = [pd.to_datetime(entry['date']) for entry in metrics['prediction_history']]
            
            if dates:
                # Create timeline showing prediction changes
                unique_predictions = []
                change_dates = []
                current_prediction = None
                
                for entry in metrics['prediction_history']:
                    if entry['predicted_leader'] != current_prediction:
                        unique_predictions.append(entry['predicted_leader'])
                        change_dates.append(pd.to_datetime(entry['date']))
                        current_prediction = entry['predicted_leader']
                
                # Plot prediction timeline
                plt.subplot(2, 2, i+1)
                if change_dates:
                    plt.plot(change_dates, range(len(change_dates)), 'o-', label=award_titles[award])
                    plt.yticks(range(len(unique_predictions)), unique_predictions)
                    plt.title(f"{award_titles[award]} Prediction Timeline")
                    plt.xlabel("Date")
                    plt.ylabel("Predicted Winner")
                    plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{output_path}/prediction_timeline_chart.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✓ Accuracy charts created successfully")
        
    except Exception as e:
        print(f"Error creating accuracy charts: {e}")

def create_accuracy_html_report():
    """Create HTML report showing prediction accuracy"""
    try:
        # Load accuracy data
        with open(f"{output_path}/prediction_accuracy_report.json", "r") as f:
            accuracy_data = json.load(f)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en" data-theme="light">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prediction Accuracy Report</title>
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
                
                .status-correct {{
                    background-color: #28a745;
                    color: #fff;
                }}
                
                .status-incorrect {{
                    background-color: #dc3545;
                    color: #fff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MLB Award Prediction Accuracy Report</h1>
                <p>Track how well our MVP and Cy Young predictions performed throughout the 2025 season.</p>
                
                <div class="accuracy-card">
                    <h2>Overall Prediction Summary</h2>
                    <p><strong>Total Prediction Days:</strong> {accuracy_data['total_predictions']}</p>
                    <p><strong>Tracking Period:</strong> 2025 MLB Season</p>
                    <p><strong>Awards Tracked:</strong> AL MVP, NL MVP, AL Cy Young, NL Cy Young</p>
                </div>
                
                <div class="accuracy-grid">
        """
        
        award_titles = {
            'al_mvp': 'AL MVP',
            'nl_mvp': 'NL MVP',
            'al_cy': 'AL Cy Young', 
            'nl_cy': 'NL Cy Young'
        }
        
        for award, metrics in accuracy_data['accuracy_by_award'].items():
            status_class = 'status-tbd'
            if metrics['final_accuracy'] == 'Correct':
                status_class = 'status-correct'
            elif metrics['final_accuracy'] == 'Incorrect':
                status_class = 'status-incorrect'
            
            html_content += f"""
                    <div class="accuracy-card">
                        <h3>{award_titles[award]}</h3>
                        <div class="accuracy-percentage">{metrics['accuracy_percentage']:.1f}%</div>
                        <p>Daily Accuracy Rate</p>
                        <div class="status-badge {status_class}">{metrics['final_accuracy']}</div>
                        <p><strong>Prediction Days:</strong> {metrics['total_days']}</p>
                        <p><strong>Correct Predictions:</strong> {metrics['correct_predictions']}</p>
                    </div>
            """
        
        html_content += """
                </div>
                
                <div class="chart-container">
                    <h2>Prediction Accuracy Analysis</h2>
                    <img src="prediction_accuracy_chart.png" alt="Prediction Accuracy Chart">
                </div>
                
                <div class="chart-container">
                    <h2>Prediction Timeline</h2>
                    <img src="prediction_timeline_chart.png" alt="Prediction Timeline Chart">
                </div>
                
                <div class="accuracy-card">
                    <h2>How to Interpret These Results</h2>
                    <p><strong>Daily Accuracy Rate:</strong> Percentage of days our algorithm correctly predicted the eventual winner.</p>
                    <p><strong>Final Accuracy:</strong> Whether our final prediction (closest to award announcement) was correct.</p>
                    <p><strong>Prediction Timeline:</strong> Shows how our predictions changed throughout the season.</p>
                    <p><strong>Methodology:</strong> Predictions are based on statistical performance, team success, and historical voting patterns.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(f"{output_path}/prediction_accuracy.html", "w") as f:
            f.write(html_content)
        
        print("✓ Accuracy HTML report created")
        
    except Exception as e:
        print(f"Error creating accuracy HTML report: {e}")

if __name__ == "__main__":
    # Save today's predictions
    save_daily_predictions()
    
    # Evaluate accuracy (will show TBD until actual winners announced)
    accuracy_metrics = evaluate_prediction_accuracy()
    
    # Create HTML report
    if accuracy_metrics:
        create_accuracy_html_report()
    
    print("✓ Prediction tracking completed successfully!")
