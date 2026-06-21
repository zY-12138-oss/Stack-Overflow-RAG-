import json
from pathlib import Path

from app.models.query_log import QueryLog


class QueryLogRepository:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self._logs: list[QueryLog] = []
        self._storage_path = Path(storage_path) if storage_path else None
        self._load()

    def save(self, query_log: QueryLog) -> None:
        self._logs.append(query_log)
        self._append_to_disk(query_log)

    def list_recent(self, limit: int = 20) -> list[QueryLog]:
        return list(reversed(self._logs[-limit:]))

    def stats(self) -> dict[str, int]:
        return {"total_queries": len(self._logs)}

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        with self._storage_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                self._logs.append(QueryLog.model_validate(json.loads(line)))

    def _append_to_disk(self, query_log: QueryLog) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self._storage_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(query_log.model_dump(mode="json"), ensure_ascii=False))
            fh.write("\n")
