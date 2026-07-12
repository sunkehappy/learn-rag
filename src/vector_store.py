import logging
import os
import time

import chromadb
from chromadb import PersistentClient
from chromadb.api.types import QueryResult
from openai import OpenAI

from config import BASE_URL, CHROMA_DIR, INGEST_RESET, QWEN_API_KEY, QWEN_EMBEDDING_MODEL, validate_config
from loader import load_documents
from models import ChunkMetadata, SearchMatch
from splitter import split_documents, Chunk, normalize_chunk_lengths

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


def reset_collection():
    chroma_client = get_chroma_client()
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        logger.info("collection deleted name=%s", COLLECTION_NAME)
    except Exception as e:
        logger.warning("collection delete skipped name=%s error=%s", COLLECTION_NAME, e)


def get_indexed_chunk_ids(collection) -> set[str]:
    result = collection.get(include=[])
    ids = result.get("ids") or []
    return set(ids)


def index_chunks(chunks: list[Chunk], batch_size: int = 10):
    chunks = normalize_chunk_lengths(chunks)
    collection = get_collection()
    existing_ids = get_indexed_chunk_ids(collection)
    pending_chunks = [chunk for chunk in chunks if chunk.id not in existing_ids]
    skipped_count = len(chunks) - len(pending_chunks)

    if skipped_count:
        logger.info(
            "index resume already_indexed=%d pending=%d total=%d",
            skipped_count,
            len(pending_chunks),
            len(chunks),
        )

    if not pending_chunks:
        logger.info("index complete nothing_to_do total=%d", len(chunks))
        return

    total = len(pending_chunks)
    total_batches = (total + batch_size - 1) // batch_size
    logger.info("index start chunk_count=%d batch_size=%d total_batches=%d", total, batch_size, total_batches)

    for batch_index, i in enumerate(range(0, total, batch_size), start=1):
        batch = pending_chunks[i:i+batch_size]
        ids = [chunk.id for chunk in batch]
        texts = [chunk.text for chunk in batch]
        embeddings = embed_texts(texts)
        metadata = [ChunkMetadata.from_chunk(chunk).to_chroma_dict() for chunk in batch]
        collection.add(ids=ids, documents=texts, embeddings=list(embeddings), metadatas=list(metadata))

        indexed = min(i + batch_size, total)
        logger.info("index progress batch=%d/%d indexed=%d/%d", batch_index, total_batches, indexed, total)

    logger.info(
        "index complete newly_indexed=%d already_indexed=%d total=%d",
        len(pending_chunks),
        skipped_count,
        len(chunks),
    )

  
def ingest_documents(reset: bool = False):
    validate_config()
    logger.info("ingest start reset=%s", reset)
    if reset:
        reset_collection()
    documents = load_documents()
    chunks = split_documents(documents)
    index_chunks(chunks)
    logger.info("ingest complete document_count=%d chunk_count=%d", len(documents), len(chunks))


def format_query_results(results: QueryResult) -> list[SearchMatch]:
    matches: list[SearchMatch] = []
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
            SearchMatch.from_chroma_row(
                chunk_id=chunk_id,
                text=text,
                raw_metadata=raw_metadata,
                distance=distance,
            )
        )
    return matches


def search_chunks(query: str, top_k: int = 3) -> list[SearchMatch]:
    logger.info("search start query=%r top_k=%d", query, top_k)
    start_time = time.perf_counter()
    collection = get_collection()
    query_embedding = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    matches = format_query_results(results)
    latency_ms = (time.perf_counter() - start_time) * 1000

    if matches:
        top_source = matches[0].metadata.document
        logger.info('-' * 80)
        logger.info(
            "search done match_count=%d top_source=%s latency_ms=%.1f",
            len(matches),
            top_source,
            latency_ms,
        )
        for match in matches:
            logger.info("match_id=%s match_text=%s match_distance=%.2f", match.id, match.text, match.distance)
    else:
        logger.info('-' * 80)
        logger.warning("search returned no matches query=%r", query)
    return matches


def main():
    from logging_config import setup_logging

    setup_logging()
    ingest_documents(reset=INGEST_RESET)
    results = search_chunks("怎么请病假，扣钱吗？")
    logger.info("search sample result_count=%d", len(results))


if __name__ == "__main__":
    main()