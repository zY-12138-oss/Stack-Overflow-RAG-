from app.providers.embedding.mock_embedding_provider import MockEmbeddingProvider
from app.providers.vector_store.factory import build_vector_store
from app.repositories.document_repository import DocumentRepository
from app.services.retrieval_service import RetrievalService


def test_dual_retrieval_merges_routes() -> None:
    service = RetrievalService(
        repository=DocumentRepository(),
        vector_store=build_vector_store(),
        embedding_provider=MockEmbeddingProvider(),
    )
    docs = service.repository.load_seed_documents()
    service.build_index(docs)

    route_results = service.retrieve_dual(
        primary_query="redis bulk write deserialization error TValue",
        secondary_query="Redis 批量写入后反序列化报错怎么办",
        top_k=5,
        keyword_candidates=service.retrieve_by_keywords(
            keywords=["Redis"],
            error_terms=["error"],
            versions=[],
            top_k=3,
        ),
    )
    merged = service.merge_results(route_results, top_k=5)

    assert route_results["rewrite_to_en"]
    assert route_results["zh_query"]
    assert route_results["keyword"]
    assert merged
    assert any(len(item.get("routes", [])) >= 1 for item in merged)


def test_keyword_recall_finds_matching_documents() -> None:
    service = RetrievalService(
        repository=DocumentRepository(),
        vector_store=build_vector_store(),
        embedding_provider=MockEmbeddingProvider(),
    )

    results = service.retrieve_by_keywords(
        keywords=["FastAPI", "upload"],
        error_terms=[],
        versions=[],
        top_k=5,
    )

    assert results
    assert any("fastapi" in item["document"].title.lower() or "fastapi" in item["document"].content.lower() for item in results)
