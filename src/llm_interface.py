from gpt4all import GPT4All
import config
from config import llm_model_path
import logging
import re
import os

logger = logging.getLogger(__name__)

llm = []
try:
    # Retrieve the model path from environment variable
    abs_llm_model_path = os.path.join(os.path.dirname(__file__), os.getenv('LLM_MODEL_PATH'))
    # Load the model once at module level
    llm = GPT4All(abs_llm_model_path, device="cpu",verbose=False,allow_download=False)
    #llm = GPT4All(llm_model_path, device="kompute",verbose=False,allow_download=False)
except Exception as e:
    logger.info(f"An unexpected error occurred while loading the llm model. The file is probably missing: {e}")


# Dictionary of prompts, where each metric's prompt is a lambda function that takes content, question, and context
metric_prompts = {
    "truthfulness": lambda content, question, conversation_context: f""" You are an AI specialized in evaluating chatbot truthfulness. Your task is to rate the truthfulness of the following chatbot message with the most appropriate word from this set: (negative, neutral, positive).
    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the truthfulness or not of the message.
    \nMessage: {content}\nUser: {question}\nContext: {conversation_context}
    """,

    "relevance": lambda content, question, conversation_context: f""" You are an AI specialized in evaluating chatbot relevance. Your task is to rate the relevance of the following message with the most appropriate word from this set: (negative, neutral, positive).
    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the relevance or not of the message.
    \nMessage: {content}\nUser: {question}\nContext: {conversation_context}
    """,

    "accuracy": lambda content, question, conversation_context: f""" You are an AI specialized in evaluating chatbot accuracy. Your task is to rate the accuracy of the following message with the most appropriate word from this set: (negative, neutral, positive).
    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the accuracy or not of the message.
    \nMessage: {content}\nUser: {question}\nContext: {conversation_context}
    """,

    "context": lambda content, question, conversation_context: f""" You are an AI specialized in evaluating chatbot responses for contextual fit. Your task is to rate how well the following message fits the conversation context with the most appropriate word from this set: (negative, neutral, positive).
    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about how the message fits in the context or not.
    \nMessage: {content}\nUser: {question}\nContext: {conversation_context}
    """,

    "response_conciseness": lambda content, question, conversation_context: f""" You are an AI specialized in evaluating the conciseness of chatbot responses. Your task is to rate how concise the following message is with the most appropriate word from this set: (negative, neutral, positive).
    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the conciseness or not of the message.
    \nMessage: {content}\nUser: {question}\nContext: {conversation_context}
    """,

    "hallucination": lambda content, question, conversation_context: f""" You are an AI specialized in detecting hallucinations in chatbot responses. Your task is to rate the degree of hallucination in the message with the most appropriate word from this set: (negative, neutral, positive).
    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the hallucination or not in the response.
    \nMessage: {content}\nUser: {question}\nContext: {conversation_context}
    """,

    "multi_query_accuracy": lambda content, question, conversation_context: f""" You are an AI specialized in evaluating multi-query accuracy. Your task is to rate the accuracy of a chatbot's response when handling multiple queries in the same conversation. Use the most appropriate word from this set: (negative, neutral, positive).
    Instructions:
    - Respond with one word: negative, neutral, or positive, followed by one short sentence explaining your choice about the accuracy in handling multiple queries.
    \nMessage: {content}\nUser: {question}\nContext: {conversation_context}
    """
}

def gpt_query(prompt):
    """Generate a response using the GPT-4All model and return the sentiment score."""
    with llm.chat_session():
        # Generate a response from the model using the given prompt
        # and limit the response to 30 tokens, then strip any whitespace
        response = llm.generate(prompt, max_tokens=20).strip()

    # Use regex to search for a sentiment label in the response (negative, neutral, or positive)
    match = re.search(r'(negative|neutral|positive)', response, re.IGNORECASE)
    score = {"negative": 0, "neutral": 0.5, "positive": 1}.get(match.group(0).lower(), -1) if match else -1
    return score, response
