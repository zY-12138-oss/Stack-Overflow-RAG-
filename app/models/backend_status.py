from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class BackendStatus:
    name: str
    backend: str
    configured: bool
    available: bool
    degraded_to: str | None = None
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
