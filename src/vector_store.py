import logging
import os
import time
from typing import Any

import chromadb
from chromadb import PersistentClient
from chromadb.api.types import QueryResult
from openai import OpenAI

from config import BASE_URL, CHROMA_DIR, QWEN_API_KEY, QWEN_EMBEDDING_MODEL, validate_config
from loader import load_documents
from splitter import split_documents, Chunk

logger = logging.getLogger(__name__)


COLLECTION_NAME = "smart_kb_chunks"

client = OpenAI(api_key=QWEN_API_KEY, base_url=BASE_URL)


def get_chroma_client():
    return PersistentClient(path=CHROMA_DIR)


def get_collection():
    chroma_client = get_chroma_client()
    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    start_time = time.perf_counter()
    response = client.embeddings.create(input=texts, model=str(QWEN_EMBEDDING_MODEL))
    embeddings = [item.embedding for item in response.data]
    latency_ms = (time.perf_counter() - start_time) * 1000
    logger.debug(
        "embed texts count=%d model=%s latency_ms=%.1f",
        len(texts),
        QWEN_EMBEDDING_MODEL,
        latency_ms,
    )
    return embeddings


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
        logger.info("collection deleted name=%s", COLLECTION_NAME)
    except Exception as e:
        logger.warning("collection delete skipped name=%s error=%s", COLLECTION_NAME, e)


def index_chunks(chunks: list[Chunk], batch_size: int = 10):
    collection = get_collection()
    logger.info("index start chunk_count=%d batch_size=%d", len(chunks), batch_size)
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        ids = [chunk.id for chunk in batch]
        texts = [chunk.text for chunk in batch]
        embeddings = embed_texts(texts)
        metadata = [chunk_to_metadata(chunk) for chunk in batch]
        collection.add(ids=ids, documents=texts, embeddings=list(embeddings), metadatas=list(metadata))

        end = min(i + batch_size, len(chunks))
        logger.debug("index progress indexed=%d total=%d", end, len(chunks))
    logger.info("index complete chunk_count=%d", len(chunks))

  
def ingest_documents(reset: bool = False):
    validate_config()
    logger.info("ingest start reset=%s", reset)
    if reset:
        reset_collection()
    documents = load_documents()
    chunks = split_documents(documents)
    index_chunks(chunks)
    logger.info("ingest complete document_count=%d chunk_count=%d", len(documents), len(chunks))


def format_query_results(results: QueryResult) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if not results.get("ids"):
        return matches

    ids = results["ids"][0]
    documents = results.get("documents")
    metadatas = results.get("metadatas")
    distances = results.get("distances")

    for index, chunk_id in enumerate(ids):
        raw_metadata = metadatas[0][index] if metadatas and metadatas[0] else {}
        text = documents[0][index] if documents and documents[0] else ""
        distance = distances[0][index] if distances and distances[0] else None
        matches.append(
            {
                "id": chunk_id,
                "text": text or "",
                "metadata": {
                    "document": raw_metadata.get("relative_path", ""),
                    "category": raw_metadata.get("category", ""),
                    "title": raw_metadata.get("doc_title", raw_metadata.get("section", "")),
                    "section": raw_metadata.get("section", ""),
                },
                "distance": distance,
            }
        )
    return matches


def search_chunks(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    logger.info("search start query=%r top_k=%d", query, top_k)
    start_time = time.perf_counter()
    collection = get_collection()
    query_embedding = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    matches = format_query_results(results)
    latency_ms = (time.perf_counter() - start_time) * 1000
    top_source = matches[0]["metadata"]["document"] if matches else None
    logger.info(
        "search done match_count=%d top_source=%s latency_ms=%.1f",
        len(matches),
        top_source,
        latency_ms,
    )
    if not matches:
        logger.warning("search returned no matches query=%r", query)
    return matches


def main():
    from logging_config import setup_logging

    setup_logging()
    ingest_documents(reset=False)
    results = search_chunks("怎么请病假，扣钱吗？")
    logger.info("search sample result_count=%d", len(results))


if __name__ == "__main__":
    main()