from dataclasses import dataclass
from pathlib import Path

from config import DOCS_DIR
from loader import Document, load_documents

@dataclass
class Chunk:
    id: str
    text: str
    doc_title: str
    section: str
    category: str
    relative_path: Path


def split_markdown_by_h2(document: Document) -> list[Chunk]:
    chunks = []
    current_chunk = None
    index= 0
    lines = document.content.splitlines()
    while index < len(lines) and not lines[index].startswith("## "):
        index += 1
    for line in lines[index:]:
        if line.startswith("## "):
            if current_chunk:
                chunks.append(current_chunk)
            id = f"{document.relative_path.stem}::chunk-{len(chunks)}"
            title = document.title
            section = line[2:].strip()
            category = document.category
            relative_path = document.relative_path
            current_chunk = Chunk(id=id, text=line, doc_title=title, section=section, category=category, relative_path=relative_path)
        else:
            current_chunk.text += line
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    chunks = []
    for document in documents:
        chunks.extend(split_markdown_by_h2(document))
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
