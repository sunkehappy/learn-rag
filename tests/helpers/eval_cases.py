from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from config import BASE_DIR

EVAL_DIR = BASE_DIR / "eval"
FIXTURES_DIR = BASE_DIR / "tests" / "fixtures"


@dataclass
class RetrievalCase:
    id: str
    topic: str
    question: str
    expected_source: str
    expected_section: str
    expected_country_code: str | None = None
    expected_entity: str | None = None
    expected_keywords: list[str] | None = None
    search_query: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Self:
        required = ("id", "topic", "question", "expected_source", "expected_section")
        missing = [field for field in required if field not in data]
        if missing:
            raise ValueError(f"case missing fields: {', '.join(missing)}")

        keywords = data.get("expected_keywords")
        keyword_list: list[str] | None = None
        if keywords is not None:
            if not isinstance(keywords, list):
                raise ValueError("expected_keywords must be a list")
            keyword_list = [str(item) for item in keywords]

        country = data.get("expected_country_code")
        entity = data.get("expected_entity")
        search_query = data.get("search_query")
        return cls(
            id=str(data["id"]),
            topic=str(data["topic"]),
            question=str(data["question"]),
            expected_source=str(data["expected_source"]),
            expected_section=str(data["expected_section"]),
            expected_country_code=str(country) if country is not None else None,
            expected_entity=str(entity) if entity is not None else None,
            expected_keywords=keyword_list,
            search_query=str(search_query) if search_query is not None else None,
        )


def load_cases(path: Path) -> list[RetrievalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"expected JSON array in {path}")
    return [RetrievalCase.from_dict(item) for item in raw]


def load_retrieval_cases() -> list[RetrievalCase]:
    return load_cases(EVAL_DIR / "handbook_retrieval.json")


def load_rag_smoke_cases() -> list[RetrievalCase]:
    return load_cases(EVAL_DIR / "handbook_rag_smoke.json")


def load_json_fixture(name: str) -> list[dict[str, object]]:
    path = FIXTURES_DIR / name
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"expected JSON array in {path}")
    return [item for item in raw if isinstance(item, dict)]
