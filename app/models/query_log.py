from datetime import datetime

from pydantic import BaseModel, Field


class QueryLog(BaseModel):
    query_id: str
    user_query: str
    detected_language: str
    rewritten_query: str
    retrieval_routes: list[str] = Field(default_factory=list)
    retrieved_doc_ids: list[str] = Field(default_factory=list)
    final_answer: str
    latency_ms: int
    llm_model: str
    embedding_model: str
    cache_hit: bool = False
    created_at: datetime
