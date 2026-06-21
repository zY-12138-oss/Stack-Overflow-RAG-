from app.api.schemas.qa import AskResponse, CitationItem, DebugInfo
from app.services.cache_service import CacheService


def test_cache_service_returns_none_when_missing() -> None:
    cache = CacheService()

    assert cache.get("missing") is None


def test_cache_service_stores_value() -> None:
    cache = CacheService()
    cache.set("answer:test", {"ok": True}, 60)

    assert cache.get("answer:test") == {"ok": True}


def test_cache_service_persists_to_local_file(tmp_path) -> None:
    cache_file = tmp_path / "cache.json"
    cache = CacheService(storage_path=cache_file)
    response = AskResponse(
        query_id="q1",
        answer="answer",
        confidence="high",
        citations=[CitationItem(title="t", url="https://example.com")],
        notes=[],
        debug=DebugInfo(
            language="zh",
            normalized_query="n",
            rewritten_query="r",
            retrieval_routes=["rewrite_to_en"],
            retrieved_doc_ids=["d1"],
            route_results={"rewrite_to_en": ["d1"]},
            cache_hit=False,
            context_preview=None,
        ),
    )

    cache.set("answer:test", response, 60)

    reloaded = CacheService(storage_path=cache_file)
    cached = reloaded.get("answer:test")

    assert cached is not None
    assert cached.answer == "answer"
    assert cached.debug.cache_hit is False


def test_cache_service_clear_removes_memory_and_file(tmp_path) -> None:
    cache_file = tmp_path / "cache.json"
    cache = CacheService(storage_path=cache_file)
    cache.set("answer:test", {"ok": True}, 60)

    result = cache.clear()

    assert cache.get("answer:test") is None
    assert cache_file.exists() is False
    assert result["removed_entries"] == 1
    assert result["file_removed"] is True
