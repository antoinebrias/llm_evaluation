import plotly.express as px

def visualize_evaluation(eval_df, metrics_dict):
    """Visualize average evaluation scores for each metric using Plotly."""

    # Extract all metrics names
    metrics = [metric for category in metrics_dict.values() for metric in category]

    # Calculate average scores for each metric
    avg_scores = eval_df[metrics].mean()

    # Create a bar plot with Plotly
    fig = px.bar(
        x=avg_scores.index,
        y=avg_scores.values,
        title='Average Evaluation Scores for Each Metric',
        labels={'x': 'Metric', 'y': 'Score'},
    )

    fig.update_layout(
        xaxis_title='Metric',
        yaxis_title='Score',
        xaxis_tickangle=-45,
        bargap=0.2
    )

    fig.show()