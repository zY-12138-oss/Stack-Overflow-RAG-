from __future__ import annotations

import json
from pathlib import Path


class IndexStateRepository:
    def __init__(self, storage_path: str | Path) -> None:
        self._storage_path = Path(storage_path)

    def load(self) -> dict[str, str]:
        if not self._storage_path.exists():
            return {}
        raw = json.loads(self._storage_path.read_text(encoding="utf-8"))
        return {
            doc_id: str(content_hash)
            for doc_id, content_hash in raw.get("documents", {}).items()
        }

    def save_many(self, state: dict[str, str], version: str | None = None) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": version or 1,
            "documents": state,
        }
        self._storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
