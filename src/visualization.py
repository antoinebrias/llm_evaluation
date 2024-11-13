import matplotlib.pyplot as plt
import logging 

# Suppress verbose debug messages from Matplotlib
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
