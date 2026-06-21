from datetime import datetime, timezone

from app.models.query_log import QueryLog
from app.repositories.query_log_repository import QueryLogRepository


def test_query_log_repository_persists_to_local_file(tmp_path) -> None:
    log_file = tmp_path / "query_logs.jsonl"
    repository = QueryLogRepository(storage_path=log_file)
    repository.save(
        QueryLog(
            query_id="q1",
            user_query="test",
            detected_language="zh",
            rewritten_query="test en",
            retrieval_routes=["rewrite_to_en"],
            retrieved_doc_ids=["d1"],
            final_answer="ok",
            latency_ms=10,
            llm_model="mock-llm",
            embedding_model="mock-embedding",
            cache_hit=False,
            created_at=datetime.now(timezone.utc),
        )
    )

    reloaded = QueryLogRepository(storage_path=log_file)

    assert reloaded.stats()["total_queries"] == 1
    assert reloaded.list_recent(1)[0].query_id == "q1"
