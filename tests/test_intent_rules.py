from intent_config import (
    apply_requirement_rules,
    normalize_country_code,
    normalize_entity,
)
from models import QueryAnalysis


def _analysis(**kwargs) -> QueryAnalysis:
    defaults = {
        "language": "zh",
        "intent": "unknown",
        "country": None,
        "country_code": None,
        "entity": None,
        "needs_clarification": False,
        "missing_fields": [],
        "clarification_question": None,
        "search_query": "test query",
    }
    defaults.update(kwargs)
    return QueryAnalysis(**defaults)


def test_country_required_intent_missing_country():
    result = apply_requirement_rules(_analysis(intent="sick_leave"))
    assert result.needs_clarification is True
    assert result.missing_fields == ["country"]
    assert result.clarification_question is not None


def test_entity_required_intent_missing_entity():
    result = apply_requirement_rules(_analysis(intent="medical_insurance"))
    assert result.needs_clarification is True
    assert result.missing_fields == ["entity"]


def test_country_intent_with_country_code_ok():
    result = apply_requirement_rules(
        _analysis(intent="sick_leave", country="Spain", country_code="ES")
    )
    assert result.needs_clarification is False
    assert result.missing_fields == []
    assert result.country_code == "ES"


def test_entity_intent_with_normalized_entity():
    result = apply_requirement_rules(
        _analysis(intent="401k", entity="gitlab inc")
    )
    assert result.needs_clarification is False
    assert result.entity == "GitLab Inc."


def test_normalize_country_from_name():
    assert normalize_country_code("Spain", None) == "ES"
    assert normalize_country_code(None, "us") == "US"


def test_unknown_intent_no_clarification():
    result = apply_requirement_rules(_analysis(intent="unknown"))
    assert result.needs_clarification is False
