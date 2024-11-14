from llm_interface import gpt_query, llm, metric_prompts
import pandas as pd
from langfuse import Langfuse
from langfuse.decorators import langfuse_context
from config import langfuse_host,public_key,secret_key
import config
import logging
import os

logger = logging.getLogger(__name__)

logger.info("langfuse_host")
logger.info(langfuse_host)
logger.info(langfuse_host)
logger.info(public_key)
logger.info(secret_key)
logger.info(os.getenv("LANGFUSE_INIT_PROJECT_SECRET_KEY"))

import httpx
import os

# Ensure `LANGFUSE_HOST` points to the internal URL of langfuse-server in Docker
langfuse_host = os.getenv("LANGFUSE_HOST", "http://langfuse-server:3000")


# Initialize Langfuse
langfuse = Langfuse()
logger.info(langfuse.auth_check())

# Function to evaluate the message for each llm-based metric 
def evaluate_message(content, question, conversation_context, metrics_dict):
    """Evaluate a message given llm-based metrics such as truthfulness, relevance, accuracy, and context."""
    
    # Initialize the evaluation dictionary
    evaluation = {}

    # Loop over each metric and prompt
    for metric, prompt_func in metric_prompts.items():
        if metric in metrics_dict["llm-based"]:
            prompt = prompt_func(content, question, conversation_context)
            score, output = gpt_query(prompt)

            # Store the score and output in the evaluation dictionary
            evaluation[metric] = score
            evaluation[f"{metric}_output"] = output

    return evaluation

def get_metadata(current_row):
        # Metadata
    metadata = {
        "message_id": current_row["id"],
        "conversation_id": current_row["conversation_id"],
        "content": current_row["content"],
        "ordinality": current_row["ordinality"],
        "question": current_row["question"],
        "conversation_context": current_row["conversation_context"]
    }
    return metadata

# Function to evaluate all sampled messages
def evaluate_sample(sample_df,metrics_dict):
    evaluation_results = []

    for i_sample, row in sample_df.iterrows():
        logger.info(f"Row {i_sample + 1}: {row.to_dict()}")

        # Fetch the context data for metrics evaluation
        content = row['content']
        question = row['question']
        conversation_context = row['conversation_context']
        
        # Metadata
        metadata = get_metadata(row)

        # LLM-based Metrics evaluation
        llm_eval_results = evaluate_message(content, question, conversation_context, metrics_dict)


        # Non LLM-based metrics gathering
        operational_results = {}
        for metric in metrics_dict["operational"]:
            operational_results[metric] = row[metric]


        # Add metadata to evaluation_results (dataframe output)
        evaluation_results.append({
            **metadata, 
            **llm_eval_results,
            **operational_results,
        })
        
        set_trace(row, metadata, content, question, conversation_context,operational_results, llm_eval_results, metrics_dict)

    eval_df = pd.DataFrame(evaluation_results)
    return eval_df


def set_trace(row, metadata, content, question, conversation_context,operational_results, llm_eval_results, metrics_dict):
        # Set the trace for Langfuse
    logger.info("------trace debug--------")
    trace = langfuse.trace(metadata=metadata,session_id=row["bot_name"],user_id="dev")
    logger.info(trace.get_trace_url())

    # Retrieve the relevant chunks
    trace.span(
        name = "generation", input={'question': question, 'context': conversation_context}, output={'response': content}
    )

    # Fill the trace metrics
    # LLM-based metrics traces
    for metric in metrics_dict["llm-based"]:
        trace.score(name=metric, value=llm_eval_results[metric],comment = llm_eval_results[f"{metric}_output"])
    # Operational metrics traces
    for metric in metrics_dict["operational"]:
        trace.score(name=metric, value=operational_results[metric])



