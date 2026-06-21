from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any, Protocol

from app.api.schemas.qa import AskResponse


class CacheBackend(Protocol):
    def get(self, key: str) -> Any | None: ...
    def set(self, key: str, value: Any, ttl_seconds: int) -> None: ...
    def stats(self) -> dict[str, int]: ...
    def clear(self) -> dict[str, object]: ...


@dataclass
class CacheEntry:
    value: Any
    expires_at: datetime


class CacheService:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._storage_path = Path(storage_path) if storage_path else None
        self._load()

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at <= datetime.now(timezone.utc):
            self._store.pop(key, None)
            self._persist()
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = CacheEntry(
            value=value,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
        )
        self._persist()

    def stats(self) -> dict[str, int]:
        self._cleanup_expired(persist=True)
        now = datetime.now(timezone.utc)
        active = sum(1 for entry in self._store.values() if entry.expires_at > now)
        expired = len(self._store) - active
        return {"entries": active, "expired": expired}

    def clear(self) -> dict[str, object]:
        removed_entries = len(self._store)
        self._store.clear()
        file_removed = False
        if self._storage_path is not None and self._storage_path.exists():
            self._storage_path.unlink()
            file_removed = True
        return {
            "removed_entries": removed_entries,
            "file_removed": file_removed,
            "storage_path": str(self._storage_path) if self._storage_path is not None else None,
        }

    def _cleanup_expired(self, persist: bool = False) -> None:
        now = datetime.now(timezone.utc)
        expired_keys = [key for key, entry in self._store.items() if entry.expires_at <= now]
        for key in expired_keys:
            self._store.pop(key, None)
        if expired_keys and persist:
            self._persist()

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        raw = json.loads(self._storage_path.read_text(encoding="utf-8"))
        now = datetime.now(timezone.utc)
        for key, item in raw.items():
            expires_at = datetime.fromisoformat(item["expires_at"])
            if expires_at <= now:
                continue
            self._store[key] = CacheEntry(
                value=AskResponse.model_validate(item["value"]),
                expires_at=expires_at,
            )

    def _persist(self) -> None:
        if self._storage_path is None:
            return
        self._cleanup_expired()
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            key: {
                "value": entry.value.model_dump(mode="json") if hasattr(entry.value, "model_dump") else entry.value,
                "expires_at": entry.expires_at.isoformat(),
            }
            for key, entry in self._store.items()
        }
        self._storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
