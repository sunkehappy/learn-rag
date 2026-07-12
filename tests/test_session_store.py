import json

import fakeredis

from models import ClarificationSession
from session_store import SessionStore


def test_session_store_roundtrip():
    server = fakeredis.FakeServer()
    client = fakeredis.FakeRedis(server=server, decode_responses=True)
    store = SessionStore.__new__(SessionStore)
    store._ttl_seconds = 60
    store._client = client

    session = ClarificationSession(
        session_id="sess-1",
        original_question="How many sick days do I get?",
        search_query="sick leave policy",
        intent="sick_leave",
        language="en",
        country=None,
        country_code=None,
        entity=None,
        missing_fields=["country"],
        last_clarification_question="Which country are you in?",
    )

    store.save_session(session)
    assert store.has_pending_session("sess-1") is True

    loaded = store.get_session("sess-1")
    assert loaded is not None
    assert loaded.original_question == session.original_question
    assert loaded.intent == "sick_leave"
    assert loaded.missing_fields == ["country"]

    store.delete_session("sess-1")
    assert store.has_pending_session("sess-1") is False


def test_session_store_invalid_payload_deleted():
    server = fakeredis.FakeServer()
    client = fakeredis.FakeRedis(server=server, decode_responses=True)
    store = SessionStore.__new__(SessionStore)
    store._ttl_seconds = 60
    store._client = client

    client.set("smartkb:session:bad", json.dumps("not-an-object"), ex=60)
    assert store.get_session("bad") is None
    assert client.get("smartkb:session:bad") is None
