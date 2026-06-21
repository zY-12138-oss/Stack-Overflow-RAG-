from app.providers.embedding.mock_embedding_provider import MockEmbeddingProvider
from app.providers.vector_store.factory import build_vector_store
from app.repositories.document_repository import DocumentRepository
from app.services.retrieval_service import RetrievalService


def main() -> None:
    queries = [
        "Redis 批量写入后反序列化报错怎么办",
        "FastAPI upload multipart validation issue",
    ]
    repository = DocumentRepository()
    retrieval_service = RetrievalService(
        repository=repository,
        vector_store=build_vector_store(),
        embedding_provider=MockEmbeddingProvider(),
    )
    documents = repository.load_seed_documents()
    retrieval_service.build_index(documents)

    for query in queries:
        route_results = retrieval_service.retrieve_dual(query, query, top_k=3)
        merged = retrieval_service.merge_results(route_results, top_k=3)
        print(f"query: {query}")
        for route_name, results in route_results.items():
            print(f"  route={route_name}")
            for item in results:
                print(f"    - {item['document'].title} | score={item['score']:.4f}")
        print("  merged:")
        for item in merged:
            print(f"    - {item['document'].title} | score={item['score']:.4f} | routes={item.get('routes', [])}")


if __name__ == "__main__":
    main()
