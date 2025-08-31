import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configurations
MODEL_LITE = "gemini-2.5-flash-lite"
MODEL = "gemini-2.5-flash"

# Default user preferences
DEFAULT_USER_NAME = "Mehdi"
DEFAULT_MAX_URLS = 1

# Research settings
DEFAULT_SEARCH_DEPTH = "basic"
MAX_QUESTIONS = 3

# File paths
RESEARCHES_DIR = "researches"
