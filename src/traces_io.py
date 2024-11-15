import sqlite3
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random
from gpt4all import GPT4All
import re
import os
from dotenv import load_dotenv
from langfuse import Langfuse
import requests
import json
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# export and import langfuse traces function

# Load .env file for environment variables
load_dotenv()

# Retrieve Langfuse API keys from .env
public_key = os.getenv("LANGFUSE_INIT_PROJECT_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_INIT_PROJECT_SECRET_KEY")
api_base = os.getenv("LANGFUSE_HOST")
llm_model_path = os.getenv("LLM_MODEL_PATH")
db_path = os.getenv("DB_PATH")
traces_export_path = os.getenv("TRACES_EXPORT_PATH")

import httpx
import os

# Ensure `LANGFUSE_HOST` points to the internal URL of langfuse-server in Docker
langfuse_host = os.getenv("LANGFUSE_HOST", "http://langfuse-server:3000")


# Initialize Langfuse with a sample rate of 0.2
langfuse = Langfuse(sample_rate=0.2)
#langfuse.auth_check()


# Fetch traces using langfuse library method
def fetch_and_export_traces(file_path="traces.csv"):
    page = 1
    page_end = False
    # Initialize list for processed trace dictionaries
    trace_dicts = []
    
    while not page_end:
        # Fetch traces of the current page using the Langfuse client
        response = langfuse.fetch_traces(page = page)

        if response.data:        
            # Iterate over traces to transform and extract score details
            for trace in response.data:
                trace_dict = trace.dict()  # Convert trace to dictionary
                
                # Initialize variables to collect score details
                score_names = []  # List to store score names for this trace

                # Collect unique score details (name, value, comment) and store them in all_scores
                if 'scores' in trace_dict and trace_dict['scores']:
                    for score_id in trace_dict['scores']:
                        score_details = get_score(score_id)
                        if score_details:
                            score_name = score_details['name']
                            # Store score details under the score_id
                            trace_dict[f'{score_name}_id'] = score_id
                            trace_dict[f'{score_name}_value'] = score_details['value']
                            trace_dict[f'{score_name}_comment'] = score_details['comment']

                            # Add score name to the score_names list
                            score_names.append(score_name)

                # Add the list of score names as a comma-separated string
                trace_dict['score_names'] = ', '.join(score_names)

                # Append transformed trace dictionary to list
                trace_dicts.append(trace_dict)
        
        else:
            # End of page reached
            page_end = True

        # Next page
        page +=1
    
    # Determine headers dynamically, including score fields
    headers = trace_dicts[0].keys() if trace_dicts else []

    # Write the trace dictionaries to a CSV file
    with open(file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(trace_dicts)

    logger.info(f"Traces exported successfully to {file_path}")


# Function to get score details
def get_score(score_id):
    url = f"{api_base}/api/public/scores/{score_id}"
    response = requests.get(url, auth=(public_key, secret_key))  

    if response.status_code == 200:
        score_data = response.json()
        score_name = score_data.get("name")
        score_value = score_data.get("value")
        score_comment = score_data.get("comment")
        return {"name" : score_name, "value": score_value, "comment": score_comment}
    else:
        logger.info(f"Failed to retrieve score. Status Code: {response.status_code}, Response: {response.text}")
        return None

def import_traces(file_path=traces_export_path):
    # Dataframe output
    traces_df=pd.DataFrame()

    try:
        # Read the CSV file
        with open(file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)  # Create a reader for the CSV file
            
            # Iterate over each row (trace) in the CSV
            for row in reader:
                # Extract metadata and parse it (assuming it's stored as a JSON-like string)
                try:
                    # Preprocess the metadata to fix the single quote issue
                    metadata_str = row["metadata"]
                    metadata_str = fix_json_quotes(metadata_str)  # Fix the quotes
                    metadata = json.loads(metadata_str)  
                except json.JSONDecodeError:
                    metadata = {}

                # Extract other fields from the CSV row
                session_id = row["sessionId"]
                user_id = row["userId"]

                # Extract the 'question', 'context', and 'response' from metadata 
                question = metadata.get("question", "")  # Get question from metadata
                conversation_context = metadata.get("conversation_context", "")  # Get context from metadata
                response_content = metadata.get("content", "")  # Get the response from the CSV column (or metadata if available)


                # Create the Langfuse trace object
                trace = langfuse.trace(name='import',metadata=metadata, session_id=session_id, user_id=user_id)

                # retrieve the relevant chunks
                trace.span(
                    name = "generation", input={'question': question, 'context': conversation_context}, output={'response': response_content}
                )

                # Process score details if they exist
                score_names = row.get('score_names', '').split(', ')  # Extract score names
                
                # For each score name, fetch its details
                for score_name in score_names:
                    # Find the corresponding score ID from the row (assumed that it follows the naming convention)
                    score_id_field = row[f'{score_name}_id']
                    score_value_field = float(row[f'{score_name}_value'])# if row[f'{score_name}_value'].isnumeric() else row[f'{score_name}_value']
                    score_comment_field = row[f'{score_name}_comment']

                    # Fill the trace metrics
                    trace.score(name=score_name, value=score_value_field,comment = score_comment_field)

            # Convert the list of dictionaries to a DataFrame, for visualization.
            traces_df = pd.read_csv(file_path)

    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' was not found.")
    except PermissionError:
        logger.error(f"Error: Permission denied for file '{file_path}'.")
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except Exception as e:
        logger.error(f"An unexpected error in import_trace occurred: {e}")

    return traces_df

# Function to preprocess metadata to fix single quotes in JSON
def fix_json_quotes(metadata_str):
    # Step 1: Correct the key formatting (add double quotes around keys)
    metadata_str = re.sub(r"'([^']*:[^']*)'", r'"\1"', metadata_str)
    
    # Step 2: Remove the \
    metadata_str = re.sub(r"'([^']+)'", r'"\1"', metadata_str)
    return metadata_str

