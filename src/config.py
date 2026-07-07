import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DOCS_DIR = BASE_DIR / "docs"

CHROMA_DIR = BASE_DIR / 'data' / "chroma"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

def validate_config():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set")
    if not OPENAI_MODEL:
        raise ValueError("OPENAI_MODEL is not set")
    if not OPENAI_EMBEDDING_MODEL:
        raise ValueError("OPENAI_EMBEDDING_MODEL is not set")
    if not DOCS_DIR.exists():
        raise ValueError("DOCS_DIR does not exist")
    
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
