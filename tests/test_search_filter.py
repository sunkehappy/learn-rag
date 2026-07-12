from intent_config import normalize_search_query
from vector_store import _build_where_filter, _tiered_where_filters


def test_build_where_filter_country_only():
    assert _build_where_filter(country_code="ES") == {"country_code": "ES"}


def test_build_where_filter_general_country():
    assert _build_where_filter(country_code="") == {"country_code": ""}


def test_build_where_filter_entity_only():
    assert _build_where_filter(entity="GitLab Inc.") == {"entity": "GitLab Inc."}


def test_build_where_filter_both():
    assert _build_where_filter(country_code="ES", entity="GitLab Iberia s.r.l.") == {
        "$and": [
            {"country_code": "ES"},
            {"entity": "GitLab Iberia s.r.l."},
        ]
    }


def test_build_where_filter_none():
    assert _build_where_filter() is None


def test_tiered_where_filters_country_only():
    tiers = _tiered_where_filters(country_code="CN")
    labels = [label for label, _ in tiers]
    assert labels == ["specific", "general", "broad"]
    assert tiers[0][1] == {"country_code": "CN"}
    assert tiers[1][1] == {"country_code": ""}


def test_tiered_where_filters_entity_only():
    tiers = _tiered_where_filters(entity="GitLab Inc.")
    labels = [label for label, _ in tiers]
    assert labels == ["specific", "general", "broad"]
    assert tiers[1][1] == {"entity": ""}


def test_tiered_where_filters_no_filter():
    tiers = _tiered_where_filters()
    assert tiers == [("broad", None)]


def test_normalize_search_query_strips_country():
    result = normalize_search_query(
        "sick_leave",
        "sick leave China policy",
        country="China",
        country_code="CN",
    )
    assert "China" not in result
    assert "CN" not in result
    assert "sick leave" in result


def test_normalize_search_query_uses_intent_hint_when_empty():
    result = normalize_search_query("sick_leave", "")
    assert "sick time" in result.lower()
