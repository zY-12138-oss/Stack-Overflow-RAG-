from app.api.schemas.qa import AskRequest, AskResponse, CitationItem, DebugInfo
from app.models.document import Document
from app.services.qa_service import QAService


class StubPreprocessService:
    def process(self, query: str) -> dict[str, object]:
        return {
            "raw_query": query,
            "normalized_query": query,
            "language": "zh",
            "keywords": [],
            "error_terms": [],
            "versions": [],
        }


class StubRewriteService:
    def rewrite(self, normalized_query: str, language: str) -> str:
        return normalized_query


class StubRetrievalService:
    def __init__(self) -> None:
        self.embedding_provider = type("EmbeddingProvider", (), {"model_name": "stub-embedding"})()

    def retrieve_by_keywords(
        self,
        keywords: list[str],
        error_terms: list[str],
        versions: list[str],
        top_k: int,
    ) -> list[dict[str, object]]:
        return []

    def retrieve_dual(
        self,
        primary_query: str,
        secondary_query: str | None,
        top_k: int,
        keyword_candidates: list[dict[str, object]] | None = None,
    ) -> dict[str, list[dict[str, object]]]:
        document = Document(
            doc_id="doc-1",
            question_id=1,
            title="Redis deserialize issue",
            content="Check serializer compatibility.",
            tags=["redis"],
            source_url="https://stackoverflow.com/questions/1",
        )
        return {
            "rewrite_to_en": [{"document": document, "score": 0.9}],
            "zh_query": [{"document": document, "score": 0.8}],
        }

    def merge_results(
        self,
        route_results: dict[str, list[dict[str, object]]],
        top_k: int,
    ) -> list[dict[str, object]]:
        return [
            {
                "document": route_results["rewrite_to_en"][0]["document"],
                "score": 0.9,
                "route": "rewrite_to_en",
                "routes": ["rewrite_to_en", "zh_query"],
            }
        ]


class StubRerankService:
    def rerank(
        self,
        query: str,
        results: list[dict[str, object]],
        preprocess_result: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        return results


class StubContextService:
    def build_context(self, ranked_results: list[dict[str, object]], max_items: int) -> str:
        return "context"


class StubAnswerService:
    def __init__(self) -> None:
        self.llm_provider = type("LLMProvider", (), {"model_name": "stub-llm"})()

    def answer(self, query: str, context: str) -> tuple[str, str, list[str]]:
        return ("answer", "high", [])


class StubCitationService:
    def build_citations(self, ranked_results: list[dict[str, object]], max_items: int = 3) -> list[CitationItem]:
        document = ranked_results[0]["document"]
        return [CitationItem(title=document.title, url=document.source_url)]


class StubQueryLogRepository:
    def save(self, query_log) -> None:
        return None


class StubCacheService:
    def __init__(self, cached_response: AskResponse) -> None:
        self.cached_response = cached_response
        self.last_set = None

    def get(self, key: str) -> AskResponse:
        return self.cached_response

    def set(self, key: str, value: AskResponse, ttl_seconds: int) -> None:
        self.last_set = (key, value, ttl_seconds)


def test_qa_service_skips_cached_response_without_citations() -> None:
    cached_response = AskResponse(
        query_id="cached",
        answer="cached answer",
        confidence="low",
        citations=[],
        notes=[],
        debug=DebugInfo(
            language="zh",
            normalized_query="Redis",
            rewritten_query="Redis",
            retrieval_routes=["rewrite_to_en"],
            retrieved_doc_ids=[],
            route_results={},
            cache_hit=False,
            context_preview=None,
        ),
    )
    cache_service = StubCacheService(cached_response)
    service = QAService(
        preprocess_service=StubPreprocessService(),
        rewrite_service=StubRewriteService(),
        retrieval_service=StubRetrievalService(),
        rerank_service=StubRerankService(),
        context_service=StubContextService(),
        answer_service=StubAnswerService(),
        citation_service=StubCitationService(),
        query_log_repository=StubQueryLogRepository(),
        cache_service=cache_service,
    )

    response = service.ask(AskRequest(query="Redis", top_k=3, return_context=False))

    assert response.query_id != "cached"
    assert response.citations
    assert response.debug.cache_hit is False
    assert cache_service.last_set is not None


def test_merge_rewrite_signals_adds_rewritten_english_keywords() -> None:
    merged = QAService._merge_rewrite_signals(
        {
            "raw_query": "Redis 批量写入后反序列化报错怎么办",
            "normalized_query": "Redis 批量写入后反序列化报错怎么办",
            "language": "zh",
            "keywords": ["Redis"],
            "error_terms": [],
            "versions": [],
        },
        "redis bulk write deserialization error TValue",
    )

    assert "bulk" in merged["keywords"]
    assert "deserialization" in merged["keywords"]
    assert "error" in merged["error_terms"]
    assert "TValue" in merged["versions"]
