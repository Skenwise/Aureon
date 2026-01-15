# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")