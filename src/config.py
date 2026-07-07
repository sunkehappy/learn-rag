import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DOCS_DIR = BASE_DIR / "docs"

CHROMA_DIR = BASE_DIR / 'data' / "chroma"

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_MODEL = os.getenv("QWEN_MODEL")
QWEN_EMBEDDING_MODEL = os.getenv("QWEN_EMBEDDING_MODEL")
BASE_URL = os.getenv("BASE_URL")

def validate_config():
    if not QWEN_API_KEY:
        raise ValueError("QWEN_API_KEY is not set")
    if not QWEN_MODEL:
        raise ValueError("QWEN_MODEL is not set")
    if not QWEN_EMBEDDING_MODEL:
        raise ValueError("QWEN_EMBEDDING_MODEL is not set")
    if not DOCS_DIR.exists():
        raise ValueError("DOCS_DIR does not exist")
    
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
