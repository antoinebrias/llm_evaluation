from database_interface import connect_db, fetch_random_data
from evaluation import evaluate_sample
from visualization import visualize_evaluation
import pandas as pd
import os
import config
import logging
from config import db_path

logger = logging.getLogger(__name__)

def main():
    conn = connect_db(db_path)

    # Define bot configurations
    # sample_size: number of random samples from the database
    # history_depth: number of messages to be retrieved in the context
    bots = [
        {"name": "Savanna/Portal Support Bot", "sample_size": 2, "history_depth": 2},
        {"name": "ALX AiCE", "sample_size": 2, "history_depth": 2},
    ]

    # define metrics
    metrics_dict = {
        "operational":["response_time"], # Operational metrics based on quantitative data
        "llm-based":  ["truthfulness","relevance","accuracy","context"] # LLM-based metrics
    }


    for bot in bots:
        logger.info(bot['name'])

        # perform the database call, and compute operational metrics
        sample_df = fetch_random_data(conn,bot,metrics_dict)

        # evaluate llm-based metrics and return a dataframe
        eval_df = evaluate_sample(sample_df,metrics_dict)

        # Save results to CSV
        sample_df.to_csv(f'sample_{bot["name"].replace(" ", "_").replace("/", "_")}_df.csv', index=False)
        eval_df.to_csv(f'eval_{bot["name"].replace(" ", "_").replace("/", "_")}_df.csv', index=False)

    # Visualize results of the last bot
    visualize_evaluation(eval_df,metrics_dict)
    conn.close()

if __name__ == '__main__':
    main()