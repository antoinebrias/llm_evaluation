import matplotlib.pyplot as plt
import logging 
import pandas as pd
import numpy as np

# Suppress verbose debug messages from Matplotlib
logger =  logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

def visualize_evaluation(eval_df, metrics_dict):
    """Visualize average evaluation scores for each metric using Matplotlib."""

    # Extract all metrics names
    metrics = [metric for category in metrics_dict.values() for metric in category]

    # Calculate average scores for each metric
    avg_scores = eval_df[metrics].mean()

    # Create a bar plot with Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(avg_scores.index, avg_scores.values, color='skyblue')

    # Add labels and title
    plt.title('Average Evaluation Scores for Each Metric')
    plt.xlabel('Metric')
    plt.ylabel('Score')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=-45, ha='left')

    # Add gridlines for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)

    # Show the plot
    plt.tight_layout()
    plt.show()


 # Function to compute the mean scores for each metric, for each bot
def compute_score_means_by_bot(trace_df):
    # Extract all score names (assuming that the score columns follow a naming convention like 'score_name_value')
    score_names = [col.split('_')[0] for col in trace_df.columns if '_value' in col]
    
    # Group by sessionId and compute the mean for each score name
    avg_scores_by_session = {}
    for score_name in score_names:
        score_value_column = f'{score_name}_value'
        if score_value_column in trace_df.columns:
            # Group by sessionId (bot id) and calculate the mean of the score values
            avg_scores_by_session[score_name] = trace_df.groupby('sessionId')[score_value_column].mean()
    
    # Convert to a DataFrame for easier visualization
    avg_scores_df = pd.DataFrame(avg_scores_by_session)
    return avg_scores_df

# Function to visualize the mean scores by sessionId (bot id) for each metric
def visualize_score_means_by_bot(trace_df):
    try:
        # Compute the mean scores by sessionId (bot id)
        avg_scores_by_session = compute_score_means_by_bot(trace_df)

        num_metrics = len(avg_scores_by_session.columns)
        blues = plt.cm.Blues(np.linspace(0.4, 0.8, num_metrics))  # Custom range of blues
        
        # Create a bar plot for each metric
        avg_scores_by_session.plot(kind='bar', figsize=(12, 8), color=blues, width=0.8)

        # Add labels and title
        plt.title('Average Evaluation Scores for Each Metric by Bot')
        plt.xlabel('Bot')
        plt.ylabel('Mean Score')

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=0, ha='left')

        # Add gridlines for better readability
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Adjust layout to ensure everything fits well
        plt.tight_layout()

        # Save the plot as a PNG file
        plt.savefig("./bot_metrics_comparison.png")

    # close the plot to free memory 
        plt.close()
    
    except Exception as e:
        logger.error(f"An unexpected error occurred in visualize_score_means_by_bot: {e}")
