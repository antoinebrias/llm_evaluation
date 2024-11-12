import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random
from gpt4all import GPT4All
import re
import os
from dotenv import load_dotenv
from langfuse import Langfuse

# Load .env file for environment variables
load_dotenv()

# Retrieve Langfuse API keys from .env
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
api_base = os.getenv("LANGFUSE_HOST")
llm_model_path = os.getenv("LLM_MODEL_PATH")
db_path = os.getenv("DB_PATH")

# Initialize Langfuse 
langfuse = Langfuse()

# Load the GPT-4All model 
llm = GPT4All(llm_model_path, device="kompute")

# Function to connect to the SQLite database
def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Function to fetch the data from the database
def fetch_data(conn, bot_name, sample_size, history_depth):
    # We select bot messages whose ordinality is greater than zero
    main_query = """
    SELECT m.id, m.conversation_id, m.content, m.ordinality, m.created_at
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.conversation_id
    JOIN bots b ON c.bot_id = b.bot_id
    WHERE m.ordinality > 0
      AND m.machine = 1
      AND b.bot_name = ?
    ORDER BY RANDOM()
    LIMIT ?;
    """
    
    cursor = conn.cursor()
    cursor.execute(main_query, (bot_name, sample_size,))
    selected_messages = cursor.fetchall()
    
    columns = [column[0] for column in cursor.description]
    
    data_with_history = []
    
    for message in selected_messages:
        message_data = dict(zip(columns, message))
        
        context_query = """
        SELECT content, machine, ordinality, created_at
        FROM messages
        WHERE conversation_id = ?
        AND ordinality < ?
        ORDER BY ordinality DESC
        LIMIT ?;
        """
        
        cursor.execute(context_query, (message_data['conversation_id'], message_data['ordinality'], history_depth))
        history_messages = cursor.fetchall()
        
        # Initialize conversation pieces
        question = ""
        conversation_context = ""
        question_timestamp = None # Initialize question_timestamp to None to handle missing case
        
        # Identify the latest user question and the last chatbot response
        for msg in history_messages:
            if msg[1] == 0 and not question:  # User message
                question = msg[0]
                question_timestamp = msg[3]  # 'created_at' timestamp of user message
            elif question:  # Chatbot response
                #conversation_context = msg[0]
                # Build the conversation history string with "User:" or "Chatbot:" based on the machine flag
                label = "Chatbot:" if msg[1] == 1 else "User:"
                conversation_context += f"{label} {msg[0]}\n"

        
        # Append the structured message data to our list
        data_with_history.append(message_data)

        # Assign the context variables to message_data
        message_data['question'] = question
        message_data['conversation_context'] = conversation_context.strip()

        # Response time
        response_timestamp = message_data['created_at']
        message_data['response_time'] = 1 # Default response time of 1 second if no question timestamp is found

        # Calculate response time if both timestamps exist
        if question_timestamp and response_timestamp:
            # Convert to datetime objects if they are in string format
            question_timestamp = datetime.strptime(question_timestamp, "%Y-%m-%d %H:%M:%S") if isinstance(question_timestamp, str) else question_timestamp
            response_timestamp = datetime.strptime(response_timestamp, "%Y-%m-%d %H:%M:%S") if isinstance(response_timestamp, str) else response_timestamp
            
            # Calculate the time difference in seconds
            message_data['response_time'] = (response_timestamp - question_timestamp).total_seconds()

        # Assign the bot name 
        message_data['bot_name'] = bot_name

        data_with_history.append(message_data)

    sample_df = pd.DataFrame(data_with_history)
    return sample_df

# Function to evaluate the message for each metric 
def evaluate_message(content, question, conversation_context):
    truthfulness_prompt = f"""
    You are an AI specialized in evaluating chatbot responses. Your task is to rate the truthfulness of 
    the following chatbot message with the most appropriate word from this set: (negative, neutral, positive).

    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the truthfulness or not of the message.

    Message:
    {content}
    User:
    {question}
    Conversation Context:
    {conversation_context}
    """

    relevance_prompt = f"""
    You are an AI specialized in evaluating chatbot responses for relevance. Your task is to rate the relevance of 
    the following message with the most appropriate word from this set: (negative, neutral, positive).

    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the relevance or not of the message.

    Message to evaluate:
    {content}
    User:
    {question}
    Conversation context:
    {conversation_context}
    """

    accuracy_prompt = f"""
    You are an AI specialized in evaluating chatbot responses for accuracy. Your task is to rate the accuracy of 
    the following message with the most appropriate word from this set: (negative, neutral, positive).

    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the accuracy or not of the message.


    Message to evaluate:
    {content}
    User:
    {question}
    Conversation context:
    {conversation_context}
    """

    context_prompt = f"""
    You are an AI specialized in evaluating chatbot responses for contextual fit. Your task is to rate how well 
    the following message fits the conversation context with the most appropriate word from this set: (negative, neutral, positive).

    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about how the message fits in the context or not.

    Message to evaluate:
    {content}
    User:
    {question}
    Conversation context:
    {conversation_context}
    """

    # coherence_prompt = f"""
    # You are an AI specialized in evaluating chatbot responses for coherence fit. Your task is to rate how fluid 
    # the following message is in the conversation context with the most appropriate word from this set: (negative, neutral, positive).

    # Instructions:
    # - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about how the message is coherent or incoherent.

    # Message to evaluate:
    # {content}
    # User:
    # {question}
    # Conversation context:
    # {conversation_context}
    # """

    truthfulness,truthfulness_output = gpt_query(llm, truthfulness_prompt)
    relevance,relevance_output = gpt_query(llm, relevance_prompt)
    accuracy,accuracy_output = gpt_query(llm, accuracy_prompt)
    context,context_output = gpt_query(llm, context_prompt)
    #coherence,coherence_output = gpt_query(llm, context_prompt)

    evaluation = {
        'truthfulness': truthfulness,
        'relevance': relevance,
        'accuracy': accuracy,
        'context': context,
        #'coherence': coherence,
        'truthfulness_output': truthfulness_output,
        'relevance_output': relevance_output,
        'accuracy_output': accuracy_output,
        'context_output': context_output,
        #'coherence_output': coherence_output
    }
    return evaluation

def extract_sentiment_score(match):
    """ Helper function to extract sentiment score based on the match. """
    sentiment_map = {
        "negative": 0,
        "neutral": 0.5,
        "positive": 1
    }
    
    if match:
        sentiment = match.group(0).lower()  # Extract the matched sentiment (lowercased)
        return sentiment_map.get(sentiment, -1)  # Default to -1 if not found
    return -1  # Return -1 if no match found

def gpt_query(llm, prompt):
    with llm.chat_session():
        # Generate response with the model
        response = llm.generate(prompt, max_tokens=40).strip()

    # Search for "negative", "neutral", or "positive" within the noisy response
    match = re.search(r'(negative|neutral|positive)', response, re.IGNORECASE)
    
    # Print statements for debugging purposes
    print("*** prompt: ***")
    print(prompt)
    print("*** response: ***")
    print(response)  # Print actual response instead of match object
   
    
    # Get the sentiment score from the response
    score = extract_sentiment_score(match)
    print("***    score       ***")
    print(score)
    return score,response


# Function to evaluate all sampled messages
def evaluate_sample(sample_df):
    evaluation_results = []
    i_sample = 1
    
    for _, row in sample_df.iterrows():
        print(i_sample)
        i_sample += 1
        content = row['content']
        question = row['question']
        conversation_context = row['conversation_context']
        
        eval_result = evaluate_message(content, question, conversation_context)
        
        metadata = {
            "message_id": row["id"],
            "conversation_id": row["conversation_id"],
            "content": row["content"],
            "ordinality": row["ordinality"],
            "question": row["question"],
            "conversation_context": row["conversation_context"]
        }

        # Add metadata to evaluation_results and include evaluation fields
        evaluation_results.append({
            **metadata,  # Unpack metadata fields
            "truthfulness": eval_result["truthfulness"],
            "relevance": eval_result["relevance"],
            "accuracy": eval_result["accuracy"],
            "context": eval_result["context"],
            #"coherence": eval_result["coherence"],
            "truthfulness_output": eval_result["truthfulness_output"],
            "relevance_output": eval_result["relevance_output"],
            "accuracy_output": eval_result["accuracy_output"],
            "context_output": eval_result["context_output"],
            #"coherence_output": eval_result["coherence_output"],
            "response_time": row["response_time"]
        })

        
        # Set the trace for Langfuse
        trace = langfuse.trace(metadata=metadata,session_id=row["bot_name"],user_id="dev")
        
        # retrieve the relevant chunks
        trace.span(
            name = "generation", input={'question': question, 'context': conversation_context}, output={'response': content}
        )

        # Fill the trace metrics
        trace.score(name='truthfulness', value=eval_result['truthfulness'],comment = eval_result['truthfulness_output'])
        trace.score(name='relevance', value=eval_result['relevance'],comment = eval_result['relevance_output'])
        trace.score(name='accuracy', value=eval_result['accuracy'],comment = eval_result['accuracy_output'])
        trace.score(name='context', value=eval_result['context'],comment = eval_result['context_output'])
        #trace.score(name='coherence', value=eval_result['coherence'],comment = eval_result['coherence_output'])
        trace.score(name='response_time', value=row["response_time"])


    eval_df = pd.DataFrame(evaluation_results)
    return eval_df

# Function to visualize the evaluation results
def visualize_evaluation(eval_df):
    metrics = ['truthfulness', 'relevance', 'accuracy', 'context', 'response_time']
    avg_scores = eval_df[metrics].mean()

    plt.figure(figsize=(8, 6))
    avg_scores.plot(kind='bar', color='skyblue')
    plt.title('Average Evaluation Scores for Each Metric')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.show()

# Main function to run the entire process
def main(db_path):
    random.seed(42)
    conn = connect_db(db_path)
    
    bot_name = "Savanna/Portal Support Bot"
    sample_size = 100
    history_depth = 2

    sample_df = fetch_data(conn, bot_name, sample_size,history_depth)
    eval_df = evaluate_sample(sample_df)
    print(eval_df)

    sample_df.to_csv('sample_savanna_df.csv', index=False) 
    eval_df.to_csv('eval_savanna_df.csv', index=False) 

    bot_name = "ALX AiCE"
    sample_size = 100
    history_depth = 2

    sample_df = fetch_data(conn, bot_name, sample_size,history_depth)
    eval_df = evaluate_sample(sample_df)
    print(eval_df)

    sample_df.to_csv('sample_aice_df.csv', index=False) 
    eval_df.to_csv('eval_aice_df.csv', index=False) 

    visualize_evaluation(eval_df)
    conn.close()

if __name__ == '__main__':
    main(db_path)
