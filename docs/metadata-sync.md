# Metadata Sync

When chunk content is unchanged but new metadata fields (e.g. `entity`, `country_code`) were added, you can update Chroma metadata without re-running embeddings.

## Metadata-only sync

```bash
SYNC_METADATA_ONLY=true python src/vector_store.py
```

This will:

1. Load and split documents (to compute current metadata)
2. Call `collection.update()` for existing chunk IDs only
3. Skip embedding API calls and skip indexing new chunks

## Default ingest (sync + index new chunks)

```bash
python src/vector_store.py
```

This runs metadata sync first, then indexes only chunks whose IDs are not already in Chroma.

## Full rebuild

```bash
INGEST_RESET=true python src/vector_store.py
```

Deletes the collection and re-indexes from scratch.
