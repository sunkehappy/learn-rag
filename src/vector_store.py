import os
from typing import Any

import chromadb
from chromadb import PersistentClient
from openai import OpenAI

from config import BASE_URL, CHROMA_DIR, QWEN_API_KEY, QWEN_EMBEDDING_MODEL, validate_config
from loader import load_documents
from splitter import split_documents, Chunk


COLLECTION_NAME = "smart_kb_chunks"

client = OpenAI(api_key=QWEN_API_KEY, base_url=BASE_URL)


def get_chroma_client():
    return PersistentClient(path=CHROMA_DIR)


def get_collection():
    chroma_client = get_chroma_client()
    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(input=texts, model=str(QWEN_EMBEDDING_MODEL))
    response = [item.embedding for item in response.data]
    return response


def chunk_to_metadata(chunk: Chunk) -> dict:
    return {
        "id": chunk.id,
        "doc_title": chunk.doc_title,
        "section": chunk.section,
        "category": chunk.category,
        "relative_path": chunk.relative_path,
    }


def reset_collection():
    chroma_client = get_chroma_client()
    try:
      chroma_client.delete_collection(name=COLLECTION_NAME)
      print(f"Collection {COLLECTION_NAME} deleted")
    except Exception as e:
      print(f"Error deleting collection: {e}")


def index_chunks(chunks: list[Chunk], batch_size: int = 10):
    collection = get_collection()
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        ids = [chunk.id for chunk in batch]
        texts = [chunk.text for chunk in batch]
        embeddings = embed_texts(texts)
        metadata = [chunk_to_metadata(chunk) for chunk in batch]
        collection.add(ids=ids, documents=texts, embeddings=list(embeddings), metadatas=list(metadata))

        end = min(i + batch_size, len(chunks))
        print(f"Indexed {end} chunks")

  
def ingest_documents(reset: bool = False):
    validate_config()
    if reset:
        reset_collection()
    documents = load_documents()
    chunks = split_documents(documents)
    index_chunks(chunks)


def search_chunks(query: str, top_k: int = 3):
    collection = get_collection()
    query_embedding = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results


def main():
    # ingest_documents(reset=True)
    ingest_documents(reset=False)
    results = search_chunks("怎么请病假，扣钱吗？")
    print(results)


if __name__ == "__main__":
    main()