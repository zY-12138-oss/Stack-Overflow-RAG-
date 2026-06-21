from app.models.document import Document
from app.providers.embedding.mock_embedding_provider import MockEmbeddingProvider
from app.repositories.document_repository import DocumentRepository
from app.repositories.index_state_repository import IndexStateRepository
from app.services.retrieval_service import RetrievalService


class QueryDimensionMismatchVectorStore:
    supports_incremental = True

    def __init__(self) -> None:
        self.documents: list[Document] = []
        self.search_calls = 0
        self.build_calls = 0

    def build(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        self.documents = documents
        self.build_calls += 1

    def upsert_documents(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        self.documents = documents

    def delete_documents(self, doc_ids: list[str]) -> None:
        self.documents = [document for document in self.documents if document.doc_id not in doc_ids]

    def search_by_vector(self, query_embedding: list[float], top_k: int) -> list[tuple[Document, float]]:
        self.search_calls += 1
        if self.search_calls == 1:
            raise Exception("Collection expecting embedding with dimension of 32, got 256")
        return [(document, 0.9) for document in self.documents[:top_k]]


def test_retrieve_rebuilds_index_when_query_hits_dimension_mismatch(tmp_path) -> None:
    repository = DocumentRepository()
    vector_store = QueryDimensionMismatchVectorStore()
    state_repository = IndexStateRepository(storage_path=tmp_path / "index_state.json")
    service = RetrievalService(
        repository=repository,
        vector_store=vector_store,
        embedding_provider=MockEmbeddingProvider(),
        index_state_repository=state_repository,
    )

    documents = repository.load_seed_documents(force_reload=True)
    service.build_index(documents)

    results = service.retrieve("redis deserialization error", top_k=3)

    assert results
    assert vector_store.search_calls == 2
    assert vector_store.build_calls >= 1
