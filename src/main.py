from database_interface import connect_db, fetch_random_data
from evaluation import evaluate_sample
from visualization import visualize_evaluation,visualize_score_means_by_bot
import pandas as pd
import os
import config
import logging
from config import db_path,traces_export_path
from langfuse import Langfuse
from langfuse.decorators import langfuse_context
from traces_io import import_traces

logger = logging.getLogger(__name__)

def main():
    # Populating langfuse traces with previously saved traces
    saved_traces_df = import_traces(file_path=traces_export_path)

    # Visualize the mean score by bot for each metric
    visualize_score_means_by_bot(saved_traces_df)

    # Live simulation run

    # Define metrics
    metrics_dict = {
        "operational":["response_time"], # Operational metrics based on quantitative data
        "llm-based":  ["truthfulness","relevance","accuracy","context","response_conciseness"] # LLM-based metrics
        # ["truthfulness","relevance","accuracy","context","response_conciseness","hallucination","multi_query_accuracy"]
    }


    # Define bot configurations
    # sample_size: number of random samples from the database
    # history_depth: number of messages to be retrieved in the context
    bots = [
        {"name": "Bot A", "sample_size": 10, "history_depth": 2},
        {"name": "Bot B", "sample_size": 10, "history_depth": 10},
    ]

    for bot in bots:
        logger.info(bot['name'])

        try:
            # perform random database call to simulate live environment, and compute operational metrics
            sample_df = fetch_random_data(db_path,bot,metrics_dict)

            # evaluate llm-based metrics, get traces and return a dataframe
            eval_df = evaluate_sample(sample_df,metrics_dict)
        except Exception as e:
            logger.info(f"An unexpected error occurred in main: {e}")


        # Save results for the new traces to CSV
        #sample_df.to_csv(f'sample_{bot["name"].replace(" ", "_").replace("/", "_")}_df.csv', index=False)
        #eval_df.to_csv(f'eval_{bot["name"].replace(" ", "_").replace("/", "_")}_df.csv', index=False)


if __name__ == '__main__':
    main()
