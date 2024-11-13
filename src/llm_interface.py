from gpt4all import GPT4All
import config
from config import llm_model_path
import logging
import re

logger = logging.getLogger(__name__)

# Load the model once at module level
llm = GPT4All(llm_model_path, device="kompute",verbose=False)

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
    """
}

def gpt_query(prompt):
    """Generate a response using the GPT-4All model and return the sentiment score."""
    with llm.chat_session():
        # Generate a response from the model using the given prompt
        # and limit the response to 30 tokens, then strip any whitespace
        response = llm.generate(prompt, max_tokens=20).strip()

    logger.info("*** prompt ***")
    logger.info(prompt)
    logger.info("*** response ***")
    logger.info(response)

    # Use regex to search for a sentiment label in the response (negative, neutral, or positive)
    match = re.search(r'(negative|neutral|positive)', response, re.IGNORECASE)
    score = {"negative": 0, "neutral": 0.5, "positive": 1}.get(match.group(0).lower(), -1) if match else -1
    return score, response
