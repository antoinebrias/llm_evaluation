import os
from dotenv import load_dotenv
import logging


# Load .env variables
load_dotenv(dotenv_path='../.env')


# Configuration variables
db_path = os.getenv("DB_PATH")
traces_export_path = os.getenv("TRACES_EXPORT_PATH")
llm_model_path = os.getenv("LLM_MODEL_PATH")
public_key = os.getenv("LANGFUSE_INIT_PROJECT_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_INIT_PROJECT_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST")

# Set up the logger with the desired level and format
logging.basicConfig(
    level=logging.INFO,                # Minimum log level to capture
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

