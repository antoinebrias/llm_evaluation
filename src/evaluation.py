from llm_interface import gpt_query, llm, metric_prompts
import pandas as pd
from langfuse import Langfuse
import config
import logging

logger = logging.getLogger(__name__)

# Initialize Langfuse
langfuse = Langfuse()

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


# Function to evaluate all sampled messages
def evaluate_sample(sample_df,metrics_dict):
    evaluation_results = []
    i_sample = 1
    
    for _, row in sample_df.iterrows():
        logger.info("Row")
        logger.info(i_sample)
        i_sample += 1

        # Fetch the context data for metrics evaluation
        content = row['content']
        question = row['question']
        conversation_context = row['conversation_context']
        
        # Metadata
        metadata = {
            "message_id": row["id"],
            "conversation_id": row["conversation_id"],
            "content": row["content"],
            "ordinality": row["ordinality"],
            "question": row["question"],
            "conversation_context": row["conversation_context"]
        }

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
        
        # Set the trace for Langfuse
        trace = langfuse.trace(metadata=metadata,session_id=row["bot_name"],user_id="dev")
        
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

    eval_df = pd.DataFrame(evaluation_results)
    return eval_df
