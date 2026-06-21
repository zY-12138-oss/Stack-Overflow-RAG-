import logging
import re
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from app.api.schemas.qa import AskRequest, AskResponse, DebugInfo
from app.core.config import settings
from app.models.query_log import QueryLog
from app.repositories.query_log_repository import QueryLogRepository
from app.services.answer_service import AnswerService
from app.services.cache_service import CacheService
from app.services.citation_service import CitationService
from app.services.context_service import ContextService
from app.services.metrics_service import MetricsService
from app.services.preprocess_service import PreprocessService
from app.services.rerank_service import RerankService
from app.services.retrieval_service import RetrievalService
from app.services.rewrite_service import RewriteService

logger = logging.getLogger(__name__)


class QAService:
    def __init__(
        self,
        preprocess_service: PreprocessService,
        rewrite_service: RewriteService,
        retrieval_service: RetrievalService,
        rerank_service: RerankService,
        context_service: ContextService,
        answer_service: AnswerService,
        citation_service: CitationService,
        query_log_repository: QueryLogRepository,
        cache_service: CacheService | None = None,
        metrics_service: MetricsService | None = None,
    ) -> None:
        self.preprocess_service = preprocess_service
        self.rewrite_service = rewrite_service
        self.retrieval_service = retrieval_service
        self.rerank_service = rerank_service
        self.context_service = context_service
        self.answer_service = answer_service
        self.citation_service = citation_service
        self.query_log_repository = query_log_repository
        self.cache_service = cache_service
        self.metrics_service = metrics_service
        self.llm_model_name = answer_service.llm_provider.model_name
        self.embedding_model_name = retrieval_service.embedding_provider.model_name

    def ask(self, payload: AskRequest) -> AskResponse:
        start = perf_counter()
        query_id = str(uuid4())
        cache_hit = False
        if self.metrics_service is not None:
            self.metrics_service.record_request()

        preprocess_result = self.preprocess_service.process(payload.query)
        normalized_query = str(preprocess_result["normalized_query"])
        language = str(preprocess_result["language"])
        rewritten_query = self.rewrite_service.rewrite(
            normalized_query=normalized_query,
            language=language,
        )
        preprocess_result = self._merge_rewrite_signals(preprocess_result, rewritten_query)

        answer_cache_key = f"answer:{language}:{payload.top_k}:{normalized_query}"
        if settings.enable_answer_cache and self.cache_service is not None:
            cached_response = self.cache_service.get(answer_cache_key)
            if cached_response is not None:
                if cached_response.citations:
                    cache_hit = True
                    cached_response.debug.cache_hit = True
                    if self.metrics_service is not None:
                        self.metrics_service.record_cache_hit()
                    logger.info("answer cache hit for query_id=%s", query_id)
                    return cached_response
                logger.info("skip incomplete cached answer for query_id=%s", query_id)

        if self.metrics_service is not None:
            self.metrics_service.record_cache_miss()

        try:
            candidate_top_k = max(payload.top_k, settings.retrieval_candidate_k)
            keyword_candidates = []
            if settings.enable_keyword_recall:
                keyword_candidates = self.retrieval_service.retrieve_by_keywords(
                    keywords=list(preprocess_result.get("keywords", [])),
                    error_terms=list(preprocess_result.get("error_terms", [])),
                    versions=list(preprocess_result.get("versions", [])),
                    top_k=settings.keyword_candidate_k,
                )

            route_results: dict[str, list[dict[str, object]]]
            if settings.enable_dual_retrieval and language == "zh":
                route_results = self.retrieval_service.retrieve_dual(
                    primary_query=rewritten_query or normalized_query,
                    secondary_query=normalized_query,
                    top_k=candidate_top_k,
                    keyword_candidates=keyword_candidates,
                )
            else:
                route_results = {
                    "rewrite_to_en": self.retrieval_service.retrieve(
                        query=rewritten_query or normalized_query,
                        top_k=candidate_top_k,
                    )
                }
                if keyword_candidates:
                    route_results["keyword"] = keyword_candidates

            merged = self.retrieval_service.merge_results(route_results, candidate_top_k)
            ranked = self.rerank_service.rerank(payload.query, merged, preprocess_result=preprocess_result)[: payload.top_k]
            context = self.context_service.build_context(ranked, max_items=settings.rerank_max_context_docs)
            answer, confidence, notes = self.answer_service.answer(payload.query, context)
            citations = self.citation_service.build_citations(ranked)

            latency_ms = int((perf_counter() - start) * 1000)
            route_names = list(route_results.keys())
            retrieved_doc_ids = [item["document"].doc_id for item in ranked]
            route_doc_map = {
                route: [result["document"].doc_id for result in results]
                for route, results in route_results.items()
            }

            logger.info(
                "qa completed query_id=%s language=%s routes=%s cache_hit=%s docs=%s latency_ms=%s",
                query_id,
                language,
                ",".join(route_names),
                cache_hit,
                retrieved_doc_ids,
                latency_ms,
            )

            self.query_log_repository.save(
                QueryLog(
                    query_id=query_id,
                    user_query=payload.query,
                    detected_language=language,
                    rewritten_query=rewritten_query,
                    retrieval_routes=route_names,
                    retrieved_doc_ids=retrieved_doc_ids,
                    final_answer=answer,
                    latency_ms=latency_ms,
                    llm_model=self.llm_model_name,
                    embedding_model=self.embedding_model_name,
                    cache_hit=cache_hit,
                    created_at=datetime.now(timezone.utc),
                )
            )

            response = AskResponse(
                query_id=query_id,
                answer=answer,
                confidence=confidence,
                citations=citations,
                notes=notes,
                debug=DebugInfo(
                    language=language,
                    normalized_query=normalized_query,
                    rewritten_query=rewritten_query,
                    retrieval_routes=route_names,
                    retrieved_doc_ids=retrieved_doc_ids,
                    route_results=route_doc_map,
                    cache_hit=cache_hit,
                    context_preview=context[:400] if payload.return_context else None,
                ),
            )

            if settings.enable_answer_cache and self.cache_service is not None:
                self.cache_service.set(answer_cache_key, response, settings.answer_cache_ttl_seconds)

            if self.metrics_service is not None:
                self.metrics_service.record_success(latency_ms)
            return response
        except Exception:
            if self.metrics_service is not None:
                self.metrics_service.record_failure()
            raise

    @staticmethod
    def _merge_rewrite_signals(
        preprocess_result: dict[str, object],
        rewritten_query: str,
    ) -> dict[str, object]:
        rewritten_tokens = [
            token
            for token in re.split(r"[^A-Za-z0-9_+#.-]+", rewritten_query)
            if token
        ][:8]
        if not rewritten_tokens:
            return preprocess_result

        merged = dict(preprocess_result)
        existing_keywords = [str(item) for item in merged.get("keywords", [])]
        combined_keywords: list[str] = []
        seen_keywords: set[str] = set()

        for token in [*existing_keywords, *rewritten_tokens]:
            lowered = token.lower()
            if lowered in seen_keywords:
                continue
            seen_keywords.add(lowered)
            combined_keywords.append(token)

        merged["keywords"] = combined_keywords[:8]
        merged["error_terms"] = [
            token
            for token in combined_keywords
            if token.lower().endswith("exception") or "error" in token.lower()
        ]
        merged["versions"] = [
            token
            for token in combined_keywords
            if any(char.isdigit() for char in token)
            or re.fullmatch(r"T[A-Z][A-Za-z0-9]*", token)
        ]
        return merged
