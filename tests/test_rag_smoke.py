from __future__ import annotations

import os

import pytest

from ask import generate_answer
from helpers.eval_cases import load_rag_smoke_cases

pytestmark = pytest.mark.llm

_cases = load_rag_smoke_cases()


def _llm_ready() -> bool:
    return bool(os.getenv("QWEN_API_KEY")) and bool(os.getenv("QWEN_MODEL"))


@pytest.mark.parametrize(
    "case",
    _cases,
    ids=[case.id for case in _cases],
)
def test_rag_smoke_keywords(case):
    if not _llm_ready():
        pytest.skip("QWEN_API_KEY / QWEN_MODEL required for llm tests")
    if not case.expected_keywords:
        pytest.fail(f"{case.id} missing expected_keywords")

    answer, matches = generate_answer(
        case.question,
        country_code=case.expected_country_code,
        entity=case.expected_entity,
    )
    assert matches, f"no matches for {case.id}"
    sources = [match.metadata.document for match in matches]
    assert case.expected_source in sources, (
        f"{case.id}: expected source {case.expected_source!r} not in top matches {sources}"
    )
    text = answer or ""
    hits = [kw for kw in case.expected_keywords if kw in text]
    assert hits, (
        f"{case.id}: none of {case.expected_keywords} found in answer={text[:300]!r}"
    )
