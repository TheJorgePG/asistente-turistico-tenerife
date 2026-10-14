import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "gemini-3.1-flash-lite"
    TEMPERATURE = 0.3
    TOP_P = 0.9
    MAX_TOKENS = 1024
    VECTOR_STORE_PATH = "data/chroma_db"