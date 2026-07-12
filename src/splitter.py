from dataclasses import dataclass, replace
import logging

from config import EMBEDDING_MAX_INPUT_CHARS
from entity_resolver import resolve_from_path, resolve_from_section
from loader import Document, load_documents

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    id: str
    text: str
    doc_title: str
    section: str
    category: str
    relative_path: str
    entity: str = ""
    country_code: str = ""


def split_text_by_length(text: str, max_length: int) -> list[str]:
    if len(text) <= max_length:
        return [text]

    parts: list[str] = []
    current = ""

    for paragraph in text.split("\n\n"):
        if len(paragraph) > max_length:
            if current:
                parts.append(current)
                current = ""
            for start in range(0, len(paragraph), max_length):
                parts.append(paragraph[start:start + max_length])
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= max_length:
            current = candidate
        else:
            if current:
                parts.append(current)
            current = paragraph

    if current:
        parts.append(current)

    return parts


def truncate_text(text: str, max_length: int, chunk_id: str) -> str:
    if len(text) <= max_length:
        return text
    logger.warning(
        "chunk text truncated id=%s original_length=%d max_length=%d",
        chunk_id,
        len(text),
        max_length,
    )
    return text[:max_length]


def split_oversized_chunk(chunk: Chunk, max_length: int = EMBEDDING_MAX_INPUT_CHARS) -> list[Chunk]:
    if len(chunk.text) <= max_length:
        return [chunk]

    text_parts = split_text_by_length(chunk.text, max_length)
    if len(text_parts) == 1:
        return [replace(chunk, text=truncate_text(chunk.text, max_length, chunk.id))]

    return [
        Chunk(
            id=f"{chunk.id}::part-{index}",
            text=truncate_text(text, max_length, f"{chunk.id}::part-{index}"),
            doc_title=chunk.doc_title,
            section=chunk.section,
            category=chunk.category,
            relative_path=chunk.relative_path,
            entity=chunk.entity,
            country_code=chunk.country_code,
        )
        for index, text in enumerate(text_parts)
    ]


def normalize_chunk_lengths(
    chunks: list[Chunk],
    max_length: int = EMBEDDING_MAX_INPUT_CHARS,
) -> list[Chunk]:
    normalized: list[Chunk] = []
    oversized_chunk_count = 0

    for chunk in chunks:
        if len(chunk.text) <= max_length:
            normalized.append(chunk)
            continue

        oversized_chunk_count += 1
        normalized.extend(split_oversized_chunk(chunk, max_length))

    if oversized_chunk_count:
        logger.info(
            "chunk length normalize oversized=%d input_count=%d output_count=%d max_length=%d",
            oversized_chunk_count,
            len(chunks),
            len(normalized),
            max_length,
        )

    return normalized


def split_markdown_by_h2(document: Document) -> list[Chunk]:
    chunks = []
    current_chunk = None
    index= 0
    base_info = resolve_from_path(document.relative_path)
    lines = document.content.splitlines()
    while index < len(lines) and not lines[index].startswith("## "):
        index += 1
    for line in lines[index:]:
        if line.startswith("## "):
            if current_chunk:
                chunks.append(current_chunk)
            id = f"{document.relative_path}::chunk-{len(chunks)}"
            title = document.title
            section = line[2:].strip()
            category = document.category
            relative_path = document.relative_path
            entity_info = resolve_from_section(base_info, section, relative_path)
            current_chunk = Chunk(
                id=id,
                text=line,
                doc_title=title,
                section=section,
                category=category,
                relative_path=relative_path,
                entity=entity_info.entity,
                country_code=entity_info.country_code,
            )
        else:
            if current_chunk:
                current_chunk.text += line
    if current_chunk:
        chunks.append(current_chunk)
    return normalize_chunk_lengths(chunks)


def split_documents(documents: list[Document]) -> list[Chunk]:
    chunks = []
    for document in documents:
        chunks.extend(split_markdown_by_h2(document))
    logger.info(
        "documents split document_count=%d chunk_count=%d",
        len(documents),
        len(chunks),
    )
    return chunks


def main():
    documents = load_documents()
    chunks = split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks")
    for chunk in chunks:
        print(f"Chunk: {chunk.id}")
        print(f"Text: {chunk.text}")
        print(f"Document Title: {chunk.doc_title}")
        print(f"Section: {chunk.section}")
        print(f"Category: {chunk.category}")
        print(f"Relative Path: {chunk.relative_path}")
        print("-" * 100)


if __name__ == "__main__":
    main()
