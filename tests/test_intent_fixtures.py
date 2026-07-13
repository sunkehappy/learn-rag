from __future__ import annotations

import pytest

from helpers.eval_cases import load_json_fixture
from intent_config import apply_requirement_rules
from models import QueryAnalysis

_cases = load_json_fixture("intent_cases.json")


@pytest.mark.parametrize("case", _cases, ids=[str(c["id"]) for c in _cases])
def test_intent_requirement_fixtures(case: dict[str, object]):
    analysis = QueryAnalysis(
        language=str(case.get("language") or "en"),
        intent=str(case["intent"]),
        country=str(case["country"]) if case.get("country") is not None else None,
        country_code=str(case["country_code"]) if case.get("country_code") is not None else None,
        entity=str(case["entity"]) if case.get("entity") is not None else None,
        needs_clarification=False,
        missing_fields=[],
        clarification_question=None,
        search_query=str(case.get("search_query") or ""),
    )
    result = apply_requirement_rules(analysis)

    assert result.needs_clarification is bool(case["expect_needs_clarification"])

    expect_missing = case["expect_missing_fields"]
    assert isinstance(expect_missing, list)
    assert result.missing_fields == expect_missing

    if "expect_country_code" in case:
        assert result.country_code == case["expect_country_code"]
    if "expect_entity" in case:
        assert result.entity == case["expect_entity"]
    if "expect_search_query_excludes" in case:
        excludes = case["expect_search_query_excludes"]
        assert isinstance(excludes, list)
        for token in excludes:
            assert str(token) not in result.search_query
    if "expect_search_query_contains" in case:
        assert str(case["expect_search_query_contains"]).lower() in result.search_query.lower()
