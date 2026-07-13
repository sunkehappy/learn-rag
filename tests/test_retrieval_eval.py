from __future__ import annotations

import os

import pytest

from helpers.eval_cases import load_retrieval_cases
from vector_store import search_chunks

pytestmark = pytest.mark.retrieval

_cases = load_retrieval_cases()


def _chroma_ready() -> bool:
    return bool(os.getenv("QWEN_API_KEY")) and bool(os.getenv("QWEN_EMBEDDING_MODEL"))


@pytest.mark.parametrize(
    "case",
    _cases,
    ids=[case.id for case in _cases],
)
def test_retrieval_top_k_contains_expected_source(case):
    if not _chroma_ready():
        pytest.skip("QWEN_API_KEY / QWEN_EMBEDDING_MODEL required for retrieval tests")

    matches = search_chunks(
        case.search_query or case.question,
        top_k=5,
        country_code=case.expected_country_code,
        entity=case.expected_entity,
    )
    assert matches, f"no matches for {case.id}: {case.question}"
    sources = [match.metadata.document for match in matches]
    assert case.expected_source in sources, (
        f"{case.id}: expected source {case.expected_source!r} not in top-5 {sources}"
    )
