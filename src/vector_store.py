import json
import logging
import os
import time

import chromadb
from chromadb import PersistentClient
from chromadb.api.types import QueryResult
from openai import OpenAI

from config import BASE_URL, CHROMA_DIR, INGEST_RESET, QWEN_API_KEY, QWEN_EMBEDDING_MODEL, SYNC_METADATA_ONLY, validate_config
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


def sync_chunk_metadata(chunks: list[Chunk], batch_size: int = 100):
    chunks = normalize_chunk_lengths(chunks)
    collection = get_collection()
    existing_ids = get_indexed_chunk_ids(collection)
    to_update = [chunk for chunk in chunks if chunk.id in existing_ids]
    skipped_count = len(chunks) - len(to_update)

    if not to_update:
        logger.info("metadata sync complete nothing_to_update total=%d", len(chunks))
        return

    total = len(to_update)
    total_batches = (total + batch_size - 1) // batch_size
    logger.info(
        "metadata sync start update_count=%d skipped=%d total=%d batch_size=%d",
        total,
        skipped_count,
        len(chunks),
        batch_size,
    )

    for batch_index, i in enumerate(range(0, total, batch_size), start=1):
        batch = to_update[i:i + batch_size]
        ids = [chunk.id for chunk in batch]
        metadata = [ChunkMetadata.from_chunk(chunk).to_chroma_dict() for chunk in batch]
        collection.update(ids=ids, metadatas=list(metadata))

        updated = min(i + batch_size, total)
        logger.info(
            "metadata sync progress batch=%d/%d updated=%d/%d",
            batch_index,
            total_batches,
            updated,
            total,
        )

    logger.info(
        "metadata sync complete updated=%d skipped=%d total=%d",
        len(to_update),
        skipped_count,
        len(chunks),
    )


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
    logger.info("ingest start reset=%s sync_metadata_only=%s", reset, SYNC_METADATA_ONLY)
    if reset:
        reset_collection()
    documents = load_documents()
    chunks = split_documents(documents)
    sync_chunk_metadata(chunks)
    if not SYNC_METADATA_ONLY:
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


def _build_where_filter(
    country_code: str | None = None,
    entity: str | None = None,
) -> dict[str, object] | None:
    clauses: list[dict[str, object]] = []
    if country_code is not None:
        clauses.append({"country_code": country_code})
    if entity is not None:
        clauses.append({"entity": entity})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def _tiered_where_filters(
    country_code: str | None = None,
    entity: str | None = None,
) -> list[tuple[str, dict[str, object] | None]]:
    tiers: list[tuple[str, dict[str, object] | None]] = []
    seen: set[str] = set()

    def add_tier(label: str, where: dict[str, object] | None) -> None:
        key = json.dumps(where, sort_keys=True) if where is not None else "__none__"
        if key in seen:
            return
        seen.add(key)
        tiers.append((label, where))

    if country_code or entity:
        add_tier("specific", _build_where_filter(country_code, entity))

    if country_code:
        add_tier("general", _build_where_filter("", entity))
        if entity:
            add_tier("general", {"country_code": ""})

    if entity and not country_code:
        add_tier("general", _build_where_filter(None, ""))

    add_tier("broad", None)
    return tiers


def _query_collection(
    collection,
    query_embedding: list[float],
    top_k: int,
    where: dict[str, object] | None,
) -> list[SearchMatch]:
    kwargs: dict[str, object] = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
    }
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    return format_query_results(results)


def search_chunks(
    query: str,
    top_k: int = 3,
    *,
    country_code: str | None = None,
    entity: str | None = None,
) -> list[SearchMatch]:
    logger.info(
        "search start query=%r top_k=%d country_code=%r entity=%r",
        query,
        top_k,
        country_code,
        entity,
    )
    start_time = time.perf_counter()
    collection = get_collection()
    query_embedding = embed_texts([query])[0]

    tiers = _tiered_where_filters(country_code, entity)
    matches: list[SearchMatch] = []
    matched_tier = "broad"

    for tier_label, where in tiers:
        matches = _query_collection(collection, query_embedding, top_k, where)
        if matches:
            matched_tier = tier_label
            if tier_label != tiers[0][0]:
                logger.warning(
                    "search tier fallback tier=%s query=%r country_code=%r entity=%r",
                    tier_label,
                    query,
                    country_code,
                    entity,
                )
            break

    latency_ms = (time.perf_counter() - start_time) * 1000

    if matches:
        top_source = matches[0].metadata.document
        logger.info('-' * 80)
        logger.info(
            "search done tier=%s match_count=%d top_source=%s latency_ms=%.1f",
            matched_tier,
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
    if SYNC_METADATA_ONLY:
        logger.info("sync metadata only mode enabled, skipping sample search")
        return
    results = search_chunks("怎么请病假，扣钱吗？")
    logger.info("search sample result_count=%d", len(results))


if __name__ == "__main__":
    main()