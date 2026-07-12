import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DOCS_DIR = BASE_DIR / "docs"
GITLAB_DOCS_DIR = DOCS_DIR / "gitlab_handbook"

CHROMA_DIR = BASE_DIR / 'data' / "chroma"

# Qwen text-embedding-v4 single-input limit is 33000 chars; keep a safety margin.
EMBEDDING_MAX_INPUT_CHARS = int(os.getenv("EMBEDDING_MAX_INPUT_CHARS", "32000"))
INGEST_RESET = os.getenv("INGEST_RESET", "false").lower() in ("1", "true", "yes")

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
