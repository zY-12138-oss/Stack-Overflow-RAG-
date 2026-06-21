import json
from pathlib import Path

from app.providers.embedding.mock_embedding_provider import MockEmbeddingProvider
from app.providers.vector_store.factory import build_vector_store
from app.repositories.document_repository import DocumentRepository
from app.services.retrieval_service import RetrievalService
from app.services.rerank_service import RerankService


EVAL_PATH = Path("evals/retrieval_eval_set.json")


def main() -> None:
    cases = json.loads(EVAL_PATH.read_text(encoding="utf-8-sig"))
    retrieval_service = RetrievalService(
        repository=DocumentRepository(),
        vector_store=build_vector_store(),
        embedding_provider=MockEmbeddingProvider(),
    )
    rerank_service = RerankService()
    docs = retrieval_service.repository.load_seed_documents()
    retrieval_service.build_index(docs)

    hits = 0
    for case in cases:
        route_results = retrieval_service.retrieve_dual(case["query"], case["query"], top_k=5)
        merged = retrieval_service.merge_results(route_results, top_k=5)
        ranked = rerank_service.rerank(case["query"], merged)
        top_doc_ids = [item["document"].doc_id for item in ranked[:3]]
        matched = case["expected_doc_id"] in top_doc_ids
        hits += int(matched)
        print(json.dumps({
            "query": case["query"],
            "expected_doc_id": case["expected_doc_id"],
            "top_doc_ids": top_doc_ids,
            "matched": matched,
        }, ensure_ascii=False))

    total = len(cases)
    print(json.dumps({
        "total": total,
        "hits_at_3": hits,
        "hit_rate_at_3": round(hits / total, 4) if total else 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
