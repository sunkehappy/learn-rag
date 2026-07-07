from dataclasses import dataclass
from pathlib import Path

from config import DOCS_DIR

@dataclass
class Document:
    path: Path
    relative_path: Path
    category: str
    title: str
    content: str

def load_documents(dir: Path) -> list[Document]:
    documents = []
    for file in dir.glob("**/*.md"):
        with open(file, "r") as f:
            content = f.read()
            documents.append(Document(path=file, content=content, metadata={}))
        
def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback

def load_markdown_file(path: Path) -> Document:
    with open(path, "r") as f:
        content = f.read()
        relative_path = path.relative_to(DOCS_DIR)
        category = relative_path.parent.name
        title = extract_title(content, relative_path.stem)
        return Document(path=path, relative_path=relative_path, category=category, title=title, content=content)


def load_documents() -> list[Document]:
    markdown_files = list(DOCS_DIR.glob("**/*.md"))
    markdown_files.sort()
    documents = []
    for file in markdown_files:
        documents.append(load_markdown_file(file))
    return documents


def main():
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    for document in documents:
        print(f"Document: {document.path}")
        print(f"Title: {document.title}")
        print(f"Category: {document.category}")
        print(f"Relative Path: {document.relative_path}")
        print(f"Content length: {len(document.content)}")
        print("-" * 100)

if __name__ == "__main__":
    main()

