from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class IndexCatalogRepository:
    def __init__(self, storage_path: str | Path) -> None:
        self._storage_path = Path(storage_path)

    def load(self) -> dict[str, object]:
        if not self._storage_path.exists():
            return {
                "active_version": None,
                "versions": {},
            }
        return json.loads(self._storage_path.read_text(encoding="utf-8"))

    def list_versions(self) -> dict[str, object]:
        return self.load()

    def set_active(self, version: str) -> dict[str, object]:
        data = self.load()
        versions = data.setdefault("versions", {})
        payload = versions.setdefault(version, self._build_version_payload(version))
        payload["updated_at"] = self._now_iso()
        payload["status"] = payload.get("status", "ready")
        data["active_version"] = version
        self._save(data)
        return data

    def upsert_version(self, version: str, metadata: dict[str, object] | None = None) -> dict[str, object]:
        data = self.load()
        versions = data.setdefault("versions", {})
        payload = versions.get(version, self._build_version_payload(version))
        if metadata:
            payload.update(metadata)
        payload["updated_at"] = self._now_iso()
        versions[version] = payload
        if data.get("active_version") is None:
            data["active_version"] = version
        self._save(data)
        return data

    def update_status(self, version: str, status: str, metadata: dict[str, object] | None = None) -> dict[str, object]:
        data = self.load()
        versions = data.setdefault("versions", {})
        payload = versions.get(version, self._build_version_payload(version))
        payload["status"] = status
        payload["updated_at"] = self._now_iso()
        if metadata:
            payload.update(metadata)
        versions[version] = payload
        self._save(data)
        return data

    def get_version(self, version: str) -> dict[str, object] | None:
        data = self.load()
        versions = data.get("versions", {})
        payload = versions.get(version)
        return payload if isinstance(payload, dict) else None

    def _save(self, payload: dict[str, object]) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _build_version_payload(version: str) -> dict[str, object]:
        return {
            "version": version,
            "updated_at": IndexCatalogRepository._now_iso(),
            "status": "ready",
        }

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
