from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    model_name: str = "unknown"

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
