from __future__ import annotations

import re
from hashlib import blake2b
from math import sqrt

from app.providers.embedding.base import EmbeddingProvider


class LocalHashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, vector_size: int = 256) -> None:
        self.vector_size = vector_size
        self.model_name = f"local-hash-{vector_size}d"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.vector_size
        tokens = self._tokenize(text)
        if not tokens:
            return vector

        for token in tokens:
            digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "little") % self.vector_size
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        norm = sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector
        return [value / norm for value in vector]

    def _tokenize(self, text: str) -> list[str]:
        normalized = text.strip().lower()
        if not normalized:
            return []
        return re.findall(r"[a-z0-9_+#.-]+|[\u4e00-\u9fff]", normalized)
