from app.main import build_embedding_provider
from app.providers.vector_store.factory import build_vector_store
from app.repositories.document_repository import DocumentRepository
from app.services.retrieval_service import RetrievalService


def main() -> None:
    repository = DocumentRepository()
    retrieval_service = RetrievalService(
        repository=repository,
        vector_store=build_vector_store(),
        embedding_provider=build_embedding_provider(),
    )
    docs = repository.load_seed_documents(force_reload=True)
    retrieval_service.build_index(docs)
    print(f"rebuilt vector index with {len(docs)} documents")


if __name__ == "__main__":
    main()
