from hashlib import sha256

from app.providers.embedding.base import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    model_name = "mock-token-frequency"
    vector_size = 32

    def embed(self, text: str) -> list[float]:
        digest = sha256(text.strip().lower().encode("utf-8")).digest()
        return [byte / 255.0 for byte in digest[: self.vector_size]]
