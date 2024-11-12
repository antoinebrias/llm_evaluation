import os
from dotenv import load_dotenv
import logging

# Load .env variables
load_dotenv()

# Configuration variables
db_path = os.getenv("DB_PATH")
llm_model_path = os.getenv("LLM_MODEL_PATH")
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
api_base = os.getenv("LANGFUSE_HOST")

# Set up the logger with the desired level and format
logging.basicConfig(
    level=logging.DEBUG,                # Minimum log level to capture
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)
