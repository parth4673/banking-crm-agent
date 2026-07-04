import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "banking_crm.db")
