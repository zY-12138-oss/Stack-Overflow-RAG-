from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class MetricsSnapshot:
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_latency_ms: int = 0
    qa_successes: int = 0
    qa_failures: int = 0

    @property
    def average_latency_ms(self) -> float:
        if self.qa_successes == 0:
            return 0.0
        return round(self.total_latency_ms / self.qa_successes, 2)


class MetricsService:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self._storage_path = Path(storage_path) if storage_path else None
        self._snapshot = MetricsSnapshot()
        self._load()

    def record_request(self) -> None:
        self._snapshot.total_requests += 1
        self._persist()

    def record_cache_hit(self) -> None:
        self._snapshot.cache_hits += 1
        self._persist()

    def record_cache_miss(self) -> None:
        self._snapshot.cache_misses += 1
        self._persist()

    def record_success(self, latency_ms: int) -> None:
        self._snapshot.qa_successes += 1
        self._snapshot.total_latency_ms += latency_ms
        self._persist()

    def record_failure(self) -> None:
        self._snapshot.qa_failures += 1
        self._persist()

    def snapshot(self) -> dict[str, int | float]:
        return {
            "total_requests": self._snapshot.total_requests,
            "cache_hits": self._snapshot.cache_hits,
            "cache_misses": self._snapshot.cache_misses,
            "qa_successes": self._snapshot.qa_successes,
            "qa_failures": self._snapshot.qa_failures,
            "total_latency_ms": self._snapshot.total_latency_ms,
            "average_latency_ms": self._snapshot.average_latency_ms,
        }

    def clear(self) -> dict[str, object]:
        self._snapshot = MetricsSnapshot()
        file_removed = False
        if self._storage_path is not None and self._storage_path.exists():
            self._storage_path.unlink()
            file_removed = True
        return {
            "status": "cleared",
            "file_removed": file_removed,
            "storage_path": str(self._storage_path) if self._storage_path is not None else None,
        }

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        self._snapshot = MetricsSnapshot(**payload)

    def _persist(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            json.dumps(asdict(self._snapshot), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
