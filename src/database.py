import sqlite3
import pandas as pd
import config
from datetime import datetime

def connect_db(db_path):
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(db_path)


def fetch_data(conn, bot_name, sample_size, history_depth, metrics_dict):
    """Fetch messages and historical context from the database for a specified bot."""
    # SQL query to fetch random bot messages
    main_query = """
    SELECT m.id, m.conversation_id, m.content, m.ordinality, m.created_at
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.conversation_id
    JOIN bots b ON c.bot_id = b.bot_id
    WHERE m.ordinality > 0 AND m.machine = 1 AND b.bot_name = ?
    ORDER BY RANDOM() LIMIT ?;
    """
    cursor = conn.cursor()
    cursor.execute(main_query, (bot_name, sample_size))
    selected_messages = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    
    data_with_history = []
    
    for message in selected_messages:
        message_data = dict(zip(columns, message))
        
        context_query = """
        SELECT content, machine, ordinality, created_at
        FROM messages
        WHERE conversation_id = ? AND ordinality < ?
        ORDER BY ordinality DESC LIMIT ?;
        """
        cursor.execute(context_query, (message_data['conversation_id'], message_data['ordinality'], history_depth))
        history_messages = cursor.fetchall()

        question_timestamp = None # Initialize question_timestamp to None to handle missing case

        # Construct conversation context and question
        message_data['question'], message_data['conversation_context'], question_timestamp = construct_context(history_messages)
        data_with_history.append(message_data)

        # Assign the bot name 
        message_data['bot_name'] = bot_name

        # Example of an Operational metric: response time
        for metric in metrics_dict["operational"]:
            if metric == "response_time":
                response_timestamp = message_data['created_at']
                message_data['response_time'] = 1 # Default response time of 1 second if no question timestamp is found

                # Calculate response time if both timestamps exist
                if question_timestamp and response_timestamp:
                    # Convert to datetime objects if they are in string format
                    question_timestamp = datetime.strptime(question_timestamp, "%Y-%m-%d %H:%M:%S") if isinstance(question_timestamp, str) else question_timestamp
                    response_timestamp = datetime.strptime(response_timestamp, "%Y-%m-%d %H:%M:%S") if isinstance(response_timestamp, str) else response_timestamp
                    
                    # Calculate the time difference in seconds
                    message_data['response_time'] = (response_timestamp - question_timestamp).total_seconds()

    return pd.DataFrame(data_with_history)


def construct_context(history_messages):
    """Create question and context strings from message history."""
    question = ""
    conversation_context = ""
    for msg in history_messages:
        label = "Chatbot- " if msg[1] == 1 else "User- "
        if msg[1] == 0 and not question:
            question = msg[0]
            question_timestamp = msg[3]  # 'created_at' timestamp of user message
        conversation_context += f"{label} {msg[0]}\n"
    return question, conversation_context.strip(),question_timestamp

