from __future__ import annotations

import json
import logging

import redis

from config import REDIS_URL, SESSION_TTL_SECONDS
from models import ClarificationSession

logger = logging.getLogger(__name__)

SESSION_KEY_PREFIX = "smartkb:session:"


class SessionStoreError(RuntimeError):
    pass


class SessionStore:
    def __init__(self, redis_url: str, ttl_seconds: int = SESSION_TTL_SECONDS):
        self._ttl_seconds = ttl_seconds
        try:
            self._client = redis.Redis.from_url(redis_url, decode_responses=True)
            self._client.ping()
        except redis.RedisError as exc:
            raise SessionStoreError(f"failed to connect to Redis at {redis_url}") from exc

    def _key(self, session_id: str) -> str:
        return f"{SESSION_KEY_PREFIX}{session_id}"

    def get_session(self, session_id: str) -> ClarificationSession | None:
        raw = self._client.get(self._key(session_id))
        if not raw:
            logger.info("session miss session_id=%s", session_id)
            return None
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("session payload is not a JSON object")
            session = ClarificationSession.from_dict(payload)
            logger.info(
                "session hit session_id=%s intent=%s missing_fields=%s",
                session_id,
                session.intent,
                session.missing_fields,
            )
            return session
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.warning("invalid session payload session_id=%s error=%s", session_id, exc)
            self.delete_session(session_id)
            return None

    def save_session(self, session: ClarificationSession) -> None:
        key = self._key(session.session_id)
        payload = json.dumps(session.to_dict(), ensure_ascii=False)
        try:
            self._client.set(key, payload, ex=self._ttl_seconds)
            logger.info(
                "session saved session_id=%s intent=%s ttl_seconds=%d",
                session.session_id,
                session.intent,
                self._ttl_seconds,
            )
        except redis.RedisError as exc:
            raise SessionStoreError(f"failed to save session {session.session_id}") from exc

    def delete_session(self, session_id: str) -> None:
        try:
            self._client.delete(self._key(session_id))
        except redis.RedisError as exc:
            raise SessionStoreError(f"failed to delete session {session_id}") from exc

    def has_pending_session(self, session_id: str) -> bool:
        return self.get_session(session_id) is not None


_default_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _default_store
    if _default_store is None:
        if not REDIS_URL:
            raise SessionStoreError("REDIS_URL is not set")
        _default_store = SessionStore(REDIS_URL)
    return _default_store
