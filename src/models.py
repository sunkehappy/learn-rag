from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

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


@dataclass
class QueryAnalysis:
    language: str
    intent: str
    country: str | None
    country_code: str | None
    entity: str | None
    needs_clarification: bool
    missing_fields: list[str]
    clarification_question: str | None
    search_query: str

    @classmethod
    def from_llm_json(cls, raw: Mapping[str, object]) -> QueryAnalysis:
        missing = raw.get("missing_fields")
        missing_fields = [str(item) for item in missing] if isinstance(missing, list) else []

        country = raw.get("country")
        country_code = raw.get("country_code")
        entity = raw.get("entity")
        clarification = raw.get("clarification_question")

        return cls(
            language=_as_str(raw.get("language"), "en"),
            intent=_as_str(raw.get("intent"), "unknown"),
            country=_as_str(country) if country is not None else None,
            country_code=_as_str(country_code) if country_code is not None else None,
            entity=_as_str(entity) if entity is not None else None,
            needs_clarification=bool(raw.get("needs_clarification")),
            missing_fields=missing_fields,
            clarification_question=_as_str(clarification) if clarification is not None else None,
            search_query=_as_str(raw.get("search_query")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "language": self.language,
            "intent": self.intent,
            "country": self.country,
            "country_code": self.country_code,
            "entity": self.entity,
            "needs_clarification": self.needs_clarification,
            "missing_fields": self.missing_fields,
            "clarification_question": self.clarification_question,
            "search_query": self.search_query,
        }


@dataclass
class ClarificationSession:
    session_id: str
    original_question: str
    search_query: str
    intent: str
    language: str
    country: str | None
    country_code: str | None
    entity: str | None
    missing_fields: list[str]
    last_clarification_question: str | None

    @classmethod
    def from_analysis(
        cls,
        session_id: str,
        original_question: str,
        analysis: QueryAnalysis,
    ) -> ClarificationSession:
        return cls(
            session_id=session_id,
            original_question=original_question,
            search_query=analysis.search_query or original_question,
            intent=analysis.intent,
            language=analysis.language,
            country=analysis.country,
            country_code=analysis.country_code,
            entity=analysis.entity,
            missing_fields=list(analysis.missing_fields),
            last_clarification_question=analysis.clarification_question,
        )

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> ClarificationSession:
        missing = raw.get("missing_fields")
        missing_fields = [str(item) for item in missing] if isinstance(missing, list) else []

        country = raw.get("country")
        country_code = raw.get("country_code")
        entity = raw.get("entity")
        last_question = raw.get("last_clarification_question")

        return cls(
            session_id=_as_str(raw.get("session_id")),
            original_question=_as_str(raw.get("original_question")),
            search_query=_as_str(raw.get("search_query")),
            intent=_as_str(raw.get("intent")),
            language=_as_str(raw.get("language"), "en"),
            country=_as_str(country) if country is not None else None,
            country_code=_as_str(country_code) if country_code is not None else None,
            entity=_as_str(entity) if entity is not None else None,
            missing_fields=missing_fields,
            last_clarification_question=_as_str(last_question) if last_question is not None else None,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "original_question": self.original_question,
            "search_query": self.search_query,
            "intent": self.intent,
            "language": self.language,
            "country": self.country,
            "country_code": self.country_code,
            "entity": self.entity,
            "missing_fields": self.missing_fields,
            "last_clarification_question": self.last_clarification_question,
        }


@dataclass
class AskResult:
    needs_clarification: bool
    clarification_question: str | None
    answer: str | None
    matches: list[SearchMatch] = field(default_factory=list)
    analysis: QueryAnalysis | None = None
