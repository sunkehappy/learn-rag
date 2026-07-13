from models import SearchMatch, SearchMatchMetadata


def test_search_match_from_chroma_row():
    match = SearchMatch.from_chroma_row(
        chunk_id="doc::chunk-0",
        text="hello",
        raw_metadata={
            "relative_path": "gitlab_handbook/values/_index.md",
            "category": "values",
            "doc_title": "Values",
            "section": "CREDIT",
            "entity": "",
            "country_code": "",
        },
        distance=0.12,
    )
    assert match.id == "doc::chunk-0"
    assert match.text == "hello"
    assert match.distance == 0.12
    assert isinstance(match.metadata, SearchMatchMetadata)
    assert match.metadata.document == "gitlab_handbook/values/_index.md"
    assert match.metadata.section == "CREDIT"
    assert match.metadata.title == "Values"
