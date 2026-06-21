from math import sqrt

from app.models.document import Document
from app.providers.vector_store.base import VectorStore


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0

    size = min(len(left), len(right))
    if size == 0:
        return 0.0

    numerator = sum(left[index] * right[index] for index in range(size))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._documents: list[Document] = []
        self._vectors: dict[str, list[float]] = {}

    def build(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        self._documents = documents
        self._vectors = {}
        for document, embedding in zip(documents, embeddings, strict=False):
            self._vectors[document.doc_id] = embedding

    def search_by_vector(self, query_embedding: list[float], top_k: int) -> list[tuple[Document, float]]:
        scored = []
        for document in self._documents:
            score = _cosine_similarity(query_embedding, self._vectors.get(document.doc_id, []))
            scored.append((document, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]
