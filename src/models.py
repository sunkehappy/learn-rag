from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from splitter import Chunk


def _as_str(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


@dataclass
class ChunkMetadata:
    id: str
    doc_title: str
    section: str
    category: str
    relative_path: str
    entity: str
    country_code: str

    @classmethod
    def from_chunk(cls, chunk: Chunk) -> ChunkMetadata:
        return cls(
            id=chunk.id,
            doc_title=chunk.doc_title,
            section=chunk.section,
            category=chunk.category,
            relative_path=chunk.relative_path,
            entity=chunk.entity,
            country_code=chunk.country_code,
        )

    def to_chroma_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "doc_title": self.doc_title,
            "section": self.section,
            "category": self.category,
            "relative_path": self.relative_path,
            "entity": self.entity,
            "country_code": self.country_code,
        }


@dataclass
class SearchMatchMetadata:
    document: str
    category: str
    title: str
    section: str
    entity: str
    country_code: str

    @classmethod
    def from_chroma(cls, raw: Mapping[str, object]) -> SearchMatchMetadata:
        doc_title = raw.get("doc_title")
        section = _as_str(raw.get("section"))
        return cls(
            document=_as_str(raw.get("relative_path")),
            category=_as_str(raw.get("category")),
            title=_as_str(doc_title or section),
            section=section,
            entity=_as_str(raw.get("entity")),
            country_code=_as_str(raw.get("country_code")),
        )


@dataclass
class SearchMatch:
    id: str
    text: str
    metadata: SearchMatchMetadata
    distance: float | None

    @classmethod
    def from_chroma_row(
        cls,
        chunk_id: str,
        text: str | None,
        raw_metadata: Mapping[str, object],
        distance: float | None,
    ) -> SearchMatch:
        return cls(
            id=chunk_id,
            text=text or "",
            metadata=SearchMatchMetadata.from_chroma(raw_metadata),
            distance=distance,
        )
