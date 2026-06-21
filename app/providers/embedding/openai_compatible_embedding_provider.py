from __future__ import annotations

from typing import Any

import httpx

from app.providers.embedding.base import EmbeddingProvider


class OpenAICompatibleEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        base_url: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        batch_size = 10
        all_embeddings: list[list[float]] = []
        max_chars = 8000  # safe limit for text-embedding-v3 (8192 tokens)

        for start in range(0, len(texts), batch_size):
            chunk = [t[:max_chars] for t in texts[start : start + batch_size]]
            response = httpx.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "input": chunk,
                },
                timeout=self.timeout_seconds,
            )
            if response.status_code != 200:
                response_text = response.text
                raise httpx.HTTPStatusError(
                    f"Embedding API error {response.status_code}: {response_text}",
                    request=response.request,
                    response=response,
                )
            payload = response.json()
            data: list[dict[str, Any]] = payload["data"]
            data.sort(key=lambda item: item["index"])
            all_embeddings.extend(item["embedding"] for item in data)
        return all_embeddings
