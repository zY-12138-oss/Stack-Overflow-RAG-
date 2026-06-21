import logging

from fastapi import FastAPI

from app.api.routes import admin, health, qa, ui
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.providers.embedding.base import EmbeddingProvider
from app.providers.embedding.local_hash_embedding_provider import LocalHashEmbeddingProvider
from app.providers.embedding.mock_embedding_provider import MockEmbeddingProvider
from app.providers.embedding.openai_compatible_embedding_provider import OpenAICompatibleEmbeddingProvider
from app.providers.llm.base import LLMProvider
from app.providers.llm.mock_llm_provider import MockLLMProvider
from app.providers.llm.openai_compatible_llm_provider import OpenAICompatibleLLMProvider
from app.providers.vector_store.factory import build_vector_store
from app.repositories.document_repository import DocumentRepository
from app.repositories.index_catalog_repository import IndexCatalogRepository
from app.repositories.index_state_repository import IndexStateRepository
from app.repositories.mysql_query_log_repository import MySQLQueryLogRepository
from app.repositories.query_log_repository import QueryLogRepository
from app.services.answer_service import AnswerService
from app.services.backend_health_service import BackendHealthService
from app.services.cache_service import CacheService
from app.services.citation_service import CitationService
from app.services.context_service import ContextService
from app.services.metrics_service import MetricsService
from app.services.preprocess_service import PreprocessService
from app.services.qa_service import QAService
from app.services.redis_cache_service import RedisCacheService
from app.services.rerank_service import RerankService
from app.services.retrieval_service import RetrievalService
from app.services.rewrite_service import RewriteService

logger = logging.getLogger(__name__)


def _require_value(name: str, value: str | None) -> str:
    if value:
        return value
    raise AppError(f"缺少配置项：{name}")


def build_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider_mode == "openai_compatible":
        return OpenAICompatibleEmbeddingProvider(
            api_key=_require_value(
                "SO_RAG_EMBEDDING_API_KEY 或 SO_RAG_LLM_API_KEY",
                settings.embedding_api_key or settings.llm_api_key,
            ),
            model_name=settings.embedding_model,
            base_url=settings.embedding_base_url,
            timeout_seconds=settings.embedding_timeout_seconds,
        )
    if settings.embedding_provider_mode == "mock":
        return MockEmbeddingProvider()
    return LocalHashEmbeddingProvider(vector_size=settings.local_embedding_dimensions)


def build_llm_provider() -> LLMProvider:
    if settings.provider_mode == "openai_compatible":
        return OpenAICompatibleLLMProvider(
            api_key=_require_value("SO_RAG_LLM_API_KEY", settings.llm_api_key),
            model_name=settings.llm_model,
            base_url=settings.llm_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
            rewrite_model_name=settings.rewrite_model,
        )
    return MockLLMProvider()


def build_local_cache_service() -> CacheService:
    return CacheService(storage_path=settings.local_cache_file_path_resolved)


def build_cache_service() -> CacheService | RedisCacheService:
    if settings.cache_backend == "redis":
        return RedisCacheService(
            redis_url=settings.redis_url,
            key_prefix=settings.redis_cache_prefix,
        )
    return build_local_cache_service()


def build_local_query_log_repository() -> QueryLogRepository:
    return QueryLogRepository(storage_path=settings.local_query_log_file_path_resolved)


def build_query_log_repository() -> QueryLogRepository | MySQLQueryLogRepository:
    if settings.query_log_backend == "mysql":
        return MySQLQueryLogRepository(mysql_url=settings.mysql_url)
    return build_local_query_log_repository()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="Stack Overflow RAG QA",
        version="0.3.4",
        description="Phase 3 production baseline with storage health checks and startup validation.",
    )

    document_repository = DocumentRepository()
    index_catalog_repository = IndexCatalogRepository(storage_path=settings.index_catalog_file_path_resolved)
    catalog = index_catalog_repository.upsert_version(settings.active_index_version)
    active_version = str(catalog.get("active_version") or settings.active_index_version)

    index_state_repository = IndexStateRepository(storage_path=settings.index_state_file_path_resolved)
    query_log_repository = build_query_log_repository()
    cache_service = build_cache_service()
    metrics_service = MetricsService(storage_path=settings.local_metrics_file_path_resolved)
    backend_health_service = BackendHealthService()
    vector_store = build_vector_store(version=active_version)
    embedding_provider = build_embedding_provider()
    llm_provider = build_llm_provider()

    cache_status = backend_health_service.check_redis_cache(settings.cache_backend, cache_service)
    if not cache_status.available and settings.cache_backend == "redis" and settings.degrade_on_storage_unavailable:
        logger.warning("redis cache unavailable, fallback to local_file: %s", cache_status.detail)
        cache_service = build_local_cache_service()
        cache_status.degraded_to = "local_file"

    query_log_status = backend_health_service.check_mysql_query_log(settings.query_log_backend, query_log_repository)
    if not query_log_status.available and settings.query_log_backend == "mysql" and settings.degrade_on_storage_unavailable:
        logger.warning("mysql query log unavailable, fallback to local_file: %s", query_log_status.detail)
        query_log_repository = build_local_query_log_repository()
        query_log_status.degraded_to = "local_file"

    preprocess_service = PreprocessService()
    rewrite_service = RewriteService(llm_provider=llm_provider, use_llm=settings.use_llm_for_rewrite)
    retrieval_service = RetrievalService(
        repository=document_repository,
        vector_store=vector_store,
        embedding_provider=embedding_provider,
        index_state_repository=index_state_repository,
    )
    rerank_service = RerankService()
    context_service = ContextService()
    citation_service = CitationService()
    answer_service = AnswerService(llm_provider=llm_provider)

    qa_service = QAService(
        preprocess_service=preprocess_service,
        rewrite_service=rewrite_service,
        retrieval_service=retrieval_service,
        rerank_service=rerank_service,
        context_service=context_service,
        answer_service=answer_service,
        citation_service=citation_service,
        query_log_repository=query_log_repository,
        cache_service=cache_service,
        metrics_service=metrics_service,
    )

    app.state.document_repository = document_repository
    app.state.index_catalog_repository = index_catalog_repository
    app.state.active_index_version = active_version
    app.state.query_log_repository = query_log_repository
    app.state.cache_service = cache_service
    app.state.metrics_service = metrics_service
    app.state.retrieval_service = retrieval_service
    app.state.qa_service = qa_service
    app.state.backend_status = {
        "cache": cache_status.to_dict(),
        "query_log": query_log_status.to_dict(),
    }

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(qa.router, prefix="/api/v1")
    app.include_router(admin.router, prefix="/api/v1")
    app.include_router(ui.router)

    @app.on_event("startup")
    def startup_event() -> None:
        logger.info("cache backend=%s", settings.cache_backend)
        logger.info("query log backend=%s", settings.query_log_backend)
        logger.info("resolved answer cache path=%s", settings.local_cache_file_path_resolved)
        logger.info("resolved query log path=%s", settings.local_query_log_file_path_resolved)
        logger.info("resolved metrics path=%s", settings.local_metrics_file_path_resolved)
        logger.info("resolved index state path=%s", settings.index_state_file_path_resolved)
        logger.info("resolved index catalog path=%s", settings.index_catalog_file_path_resolved)
        logger.info("active index version=%s", active_version)
        logger.info("backend status=%s", app.state.backend_status)
        docs = document_repository.load_seed_documents()
        retrieval_service.build_index(docs)

    return app


app = create_app()
