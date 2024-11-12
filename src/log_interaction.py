import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random
from gpt4all import GPT4All
import re


# Load the GPT-4All model (replace with the correct path to your model file)
#llm = GPT4All("/home/antoine/Documents/Administratif/Emploi/alx/assignment/project_brias/src/gpt4all/Meta-Llama-3-8B-Instruct.Q4_0.gguf")
llm = GPT4All("/home/antoine/Documents/Administratif/Emploi/alx/assignment/project_brias/src/gpt4all/Phi-3-mini-4k-instruct-q4.gguf",device="kompute")


# Function to connect to the SQLite database
def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Function to fetch the data from the database
def fetch_data(conn, bot_name,sample_size,history_depth):
    # Define the main SQL query to fetch sample_size random messages
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
    
    # Execute the main query to fetch the target messages
    cursor = conn.cursor()
    cursor.execute(main_query, (bot_name,sample_size,))
    selected_messages = cursor.fetchall()
    
    # Prepare columns for the main message DataFrame
    columns = [column[0] for column in cursor.description]
    
    # Initialize a list to store each message row with context
    data_with_history = []
    
    for message in selected_messages:
        # Convert each selected message into a dictionary
        message_data = dict(zip(columns, message))
        
        # Define a subquery to get previous messages in the conversation as context
        context_query = """
        SELECT content, machine, ordinality, created_at
        FROM messages
        WHERE conversation_id = ?
        AND ordinality < ?
        ORDER BY ordinality DESC
        LIMIT ?;
        """
        
        # Fetch conversation history messages for each selected message
        cursor.execute(context_query, (message_data['conversation_id'], message_data['ordinality'],history_depth))
        history_messages = cursor.fetchall()
        
        # Build the conversation history string with "User:" or "Chatbot:" based on the machine flag
        context = ""
        for msg in history_messages:
            label = "Chatbot:" if msg[1] == 1 else "User:"
            context += f"{label} {msg[0]}\n"
        
        # Add the formatted conversation history string to the message data dictionary
        message_data['conversation_history'] = context.strip()  # Strip to remove the trailing newline
        
        # Append the structured message data to our list
        data_with_history.append(message_data)
        
        # Convert the list of dictionaries to a DataFrame
        message_df = pd.DataFrame(data_with_history)
    
    return message_df

""" # Function to get a sample of messages (for evaluation)
def get_random_sample(messages_df, sample_size=2):
    # Randomly select a subset of messages

    
    sample = messages_df.sample(n=sample_size, random_state=42)
    return sample """

# Function to evaluate the message for each metric 
def evaluate_message(message_content,conversation_history):
    truthfulness_prompt = f"""
    You are an AI specialized in chatbot evaluation, that responds with a single numeric value only, strictly between 1 and 5. 
    Do not include any words, explanations, or punctuation.

    Rate the truthfulness of the following chatbot message on a scale from 1 to 5, where:
    1 = completely false, and 5 = completely true.

    Return only a numeric score (1-5), for example: 3.

    Message:
    {message_content}

    Conversation Context:
    {conversation_history}
    """

    relevance_prompt = f"""
    You are an AI specialized in chatbot evaluation, that responds with a single numeric value only, strictly between 1 and 5. 
    Do not include any words, explanations, or punctuation.

    Rate the relevance of the following chatbot message to the user's query on a scale from 1 to 5, where:
    1 = completely irrelevant, and 5 = highly relevant.

    Return only a numeric score (1-5), for example: 3.

    Message:
    {message_content}

    Conversation Context:
    {conversation_history}
    """

    accuracy_prompt = f"""
    You are an AI specialized in chatbot evaluation, that responds with a single numeric value only, strictly between 1 and 5. 
    Do not include any words, explanations, or punctuation.

    Rate the accuracy of the following chatbot message on a scale from 1 to 5, where:
    1 = completely inaccurate, and 5 = highly accurate.

    Return only a numeric score (1-5), for example: 3.

    Message:
    {message_content}

    Conversation Context:
    {conversation_history}
    """

    context_prompt = f"""
    You are an AI specialized in chatbot evaluation, that responds with a single numeric value only, strictly between 1 and 5. 
    Do not include any words, explanations, or punctuation.

    Rate how well the following chatbot message fits the context of the conversation on a scale from 1 to 5, where:
    1 = completely out of context, and 5 = highly appropriate.

    Return only a numeric score (1-5), for example: 3.

    Message:
    {message_content}

    Conversation Context:
    {conversation_history}
    """

    # Query GPT-4All for each evaluation aspect
    truthfulness = gpt_query(llm, truthfulness_prompt)
    relevance = gpt_query(llm, relevance_prompt)
    accuracy = gpt_query(llm, accuracy_prompt)
    context = gpt_query(llm, context_prompt)

    evaluation = {
        'truthfulness': truthfulness,
        'relevance': relevance,
        'accuracy': accuracy,
        'context': context
    }
    return evaluation

def extract_numeric_score(response):
    # Find all numeric sequences in the response
    numeric_values = re.findall(r'\d+', response)
    
    # Convert the first found sequence to an integer if any are found
    score = min(5,max(1,int(numeric_values[0]))) if numeric_values else -1
    return score

def gpt_query(llm, prompt):
    # Generate response from GPT-4All model
    with llm.chat_session():
        response = llm.generate(prompt, max_tokens=5)
    #print("*** prompt: ***")
    #print(prompt)
    #print("*** response: ***")
    #print(response)

    # Parse the response (assumes the model returns a numeric response)
    try:
        score = extract_numeric_score(response)
    except ValueError:
        score = -1 #random.randint(1, 5)  # In case of an error in response format
    
    return score

# Function to evaluate all sampled messages
def evaluate_sample(sample_df):
    evaluation_results = []
    i_sample=1
    
    for _, row in sample_df.iterrows():
        print(i_sample)
        i_sample += 1
        message_content = row['content']
        conversation_history = row['conversation_history']
        
        # Evaluate the message
        eval_result = evaluate_message(message_content,conversation_history)
        
        # Add evaluation result to the list
        evaluation_results.append({
            'message_id': row['id'],
            'conversation_id': row['conversation_id'],
            'content': row['content'],
            'ordinality': row['ordinality'],
            'conversation_history': row['conversation_history'],
            'truthfulness': eval_result['truthfulness'],
            'relevance': eval_result['relevance'],
            'accuracy': eval_result['accuracy'],
            'context': eval_result['context']
        })

    # Convert evaluation results to DataFrame for further analysis
    eval_df = pd.DataFrame(evaluation_results)
    return eval_df

# Function to visualize the evaluation results
def visualize_evaluation(eval_df):
    # Plot the average scores for each metric
    metrics = ['truthfulness', 'relevance', 'accuracy', 'context']
    avg_scores = eval_df[metrics].mean()

    plt.figure(figsize=(8, 6))
    avg_scores.plot(kind='bar', color='skyblue')
    plt.title('Average Evaluation Scores for Each Metric')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.show()

# Main function to run the entire process
def main(db_path):
    # Set up random seed for reproducibility
    random.seed(88)

    # Connect to the database
    conn = connect_db(db_path)

    # Bot selection
    #bot_name = "ALX AiCE"
    bot_name = "Savanna/Portal Support Bot"

    # Sample size
    sample_size = 100

    # Max number of messages to keep
    history_depth = 1

    # Fetch the data
    sample_df = fetch_data(conn, bot_name,sample_size,history_depth)

    # Evaluate the sample
    eval_df = evaluate_sample(sample_df)

    # Show the evaluation results
    print(eval_df)

    # Save data
    sample_df.to_csv('sample_df.csv', index=False) 
    eval_df.to_csv('eval_df.csv', index=False) 

    # Visualize the evaluation metrics
    visualize_evaluation(eval_df)

    # Close the database connection
    conn.close()

# Run the script with your database path
if __name__ == '__main__':
    db_path = '/home/antoine/Documents/Administratif/Emploi/alx/assignment/project_brias/data/sampled_conversations.db'  # Path to the SQLite database
    main(db_path)
