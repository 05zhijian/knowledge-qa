import os

from dotenv import load_dotenv

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
EMBED_MODEL = os.getenv("EMBED_MODEL", "embedding-2")
CHAT_MODEL = os.getenv("CHAT_MODEL", "glm-4-flash")
TOP_K = int(os.getenv("TOP_K", "3"))
DB_PATH = os.getenv("DB_PATH", "data/kb.db")
DATA_DIR = os.getenv("DATA_DIR", "data/raw")
