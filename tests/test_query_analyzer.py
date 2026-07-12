from models import ClarificationSession, QueryAnalysis
from query_analyzer import merge_clarification, parse_analyzer_response


def test_parse_analyzer_response_json():
    content = """
    {
      "language": "zh",
      "intent": "sick_leave",
      "country": null,
      "country_code": null,
      "entity": null,
      "needs_clarification": true,
      "missing_fields": ["country"],
      "clarification_question": "请问您所在的国家是哪里？",
      "search_query": "sick leave policy"
    }
    """
    analysis = parse_analyzer_response(content)
    assert analysis.intent == "sick_leave"
    assert analysis.language == "zh"
    assert analysis.missing_fields == ["country"]


def test_parse_analyzer_response_with_markdown_fence():
    content = """```json
{"language":"en","intent":"unknown","country":null,"country_code":null,"entity":null,
"needs_clarification":false,"missing_fields":[],"clarification_question":null,"search_query":""}
```"""
    analysis = parse_analyzer_response(content)
    assert analysis.intent == "unknown"
    assert analysis.needs_clarification is False


def test_parse_analyzer_response_invalid_json():
    analysis = parse_analyzer_response("not json")
    assert analysis.intent == "unknown"
    assert analysis.needs_clarification is False


def test_merge_clarification_preserves_search_query(monkeypatch):
    captured: list[str] = []

    def fake_call(user_question: str) -> QueryAnalysis:
        captured.append(user_question)
        return QueryAnalysis(
            language="en",
            intent="sick_leave",
            country="Spain",
            country_code="ES",
            entity=None,
            needs_clarification=False,
            missing_fields=[],
            clarification_question=None,
            search_query="",
        )

    monkeypatch.setattr("query_analyzer._call_analyzer", fake_call)

    session = ClarificationSession(
        session_id="sess-1",
        original_question="How many sick days?",
        search_query="sick leave days",
        intent="sick_leave",
        language="en",
        country=None,
        country_code=None,
        entity=None,
        missing_fields=["country"],
        last_clarification_question="Which country are you in?",
    )

    result = merge_clarification(session, "Spain")
    assert result.country_code == "ES"
    assert result.search_query == "sick leave days"
    assert "Original question: How many sick days?" in captured[0]
    assert "User clarification: Spain" in captured[0]
