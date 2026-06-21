from __future__ import annotations

import json
from typing import Any

from redis import Redis

from app.api.schemas.qa import AskResponse


class RedisCacheService:
    def __init__(self, redis_url: str, key_prefix: str) -> None:
        self._client = Redis.from_url(redis_url, decode_responses=True, protocol=2)
        self._key_prefix = key_prefix

    def ping(self) -> bool:
        return bool(self._client.ping())

    def get(self, key: str) -> Any | None:
        raw = self._client.get(self._build_key(key))
        if raw is None:
            return None
        return AskResponse.model_validate(json.loads(raw))

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        payload = value.model_dump(mode="json") if hasattr(value, "model_dump") else value
        self._client.set(self._build_key(key), json.dumps(payload, ensure_ascii=False), ex=ttl_seconds)

    def stats(self) -> dict[str, int]:
        count = len(self._client.keys(f"{self._key_prefix}*"))
        return {"entries": count, "expired": 0}

    def clear(self) -> dict[str, object]:
        keys = self._client.keys(f"{self._key_prefix}*")
        removed = 0
        if keys:
            removed = self._client.delete(*keys)
        return {
            "removed_entries": int(removed),
            "file_removed": False,
            "storage_path": None,
        }

    def _build_key(self, key: str) -> str:
        return f"{self._key_prefix}{key}"
