from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Stack Overflow RAG QA"
    env: str = "dev"
    log_level: str = "INFO"
    seed_data_path: str = "data/stackoverflow_2025/20250101_to_20250103/qa_merged.jsonl"
    top_k_default: int = 5
    phase_name: str = "phase-3-production"

    mock_llm_enabled: bool = True
    mock_embedding_enabled: bool = True
    use_llm_for_rewrite: bool = True

    prompt_version: str = Field(default="v1")
    retrieval_mode: str = Field(default="rewrite_to_en")
    provider_mode: str = Field(default="mock")
    embedding_provider_mode: str = Field(default="local_hash")
    vector_store_provider: str = Field(default="in_memory")
    cache_backend: str = Field(default="local_file")
    query_log_backend: str = Field(default="local_file")
    degrade_on_storage_unavailable: bool = Field(default=True)
    chroma_persist_path: str = Field(default="data/indexes/chroma")
    chroma_collection_name: str = Field(default="stack_overflow_qa")
    index_state_file_path: str = Field(default="data/indexes/index_state.json")
    index_catalog_file_path: str = Field(default="data/indexes/index_catalog.json")
    active_index_version: str = Field(default="v1")
    local_embedding_dimensions: int = 256

    redis_url: str = Field(default="redis://127.0.0.1:6379/0")
    redis_cache_prefix: str = Field(default="so_rag:answer:")

    mysql_url: str = Field(default="mysql+pymysql://root:password@127.0.0.1:3306/stack_overflow_rag")

    enable_dual_retrieval: bool = True
    enable_query_cache: bool = True
    enable_answer_cache: bool = True
    enable_keyword_recall: bool = True
    query_cache_ttl_seconds: int = 1800
    answer_cache_ttl_seconds: int = 900
    local_cache_file_path: str = Field(default="data/local_cache/answer_cache.json")
    local_query_log_file_path: str = Field(default="data/local_cache/query_logs.jsonl")
    local_metrics_file_path: str = Field(default="data/local_cache/runtime_metrics.json")
    retrieval_candidate_k: int = 8
    keyword_candidate_k: int = 5
    rerank_max_context_docs: int = 4

    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4.1-mini"
    rewrite_model: str | None = None
    llm_timeout_seconds: float = 60.0

    embedding_api_key: str | None = None
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_prefix="SO_RAG_", env_file=".env", extra="ignore")

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def resolve_path(self, value: str | Path) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return (self.project_root / path).resolve()

    @property
    def seed_data_path_resolved(self) -> Path:
        return self.resolve_path(self.seed_data_path)

    @property
    def chroma_persist_path_resolved(self) -> Path:
        return self.resolve_path(self.chroma_persist_path)

    @property
    def index_state_file_path_resolved(self) -> Path:
        return self.resolve_path(self.index_state_file_path)

    @property
    def index_catalog_file_path_resolved(self) -> Path:
        return self.resolve_path(self.index_catalog_file_path)

    @property
    def local_cache_file_path_resolved(self) -> Path:
        return self.resolve_path(self.local_cache_file_path)

    @property
    def local_query_log_file_path_resolved(self) -> Path:
        return self.resolve_path(self.local_query_log_file_path)

    @property
    def local_metrics_file_path_resolved(self) -> Path:
        return self.resolve_path(self.local_metrics_file_path)


settings = Settings()
