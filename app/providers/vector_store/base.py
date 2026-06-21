from abc import ABC, abstractmethod

from app.models.document import Document


class VectorStore(ABC):
    supports_incremental: bool = False

    @abstractmethod
    def build(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search_by_vector(self, query_embedding: list[float], top_k: int) -> list[tuple[Document, float]]:
        raise NotImplementedError

    def upsert_documents(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        raise NotImplementedError("current vector store does not support incremental upsert")

    def delete_documents(self, doc_ids: list[str]) -> None:
        raise NotImplementedError("current vector store does not support incremental delete")
