from typing import Any

from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=5, ge=1, le=10)
    return_context: bool = False


class CitationItem(BaseModel):
    title: str
    url: str

    @field_validator("url", mode="before")
    @classmethod
    def clean_url(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip("`").strip()
        return v


class DebugInfo(BaseModel):
    language: str
    normalized_query: str
    rewritten_query: str
    retrieval_routes: list[str]
    retrieved_doc_ids: list[str]
    route_results: dict[str, list[str]] = Field(default_factory=dict)
    cache_hit: bool = False
    context_preview: str | None = None


class AskResponse(BaseModel):
    query_id: str
    answer: str
    confidence: str
    citations: list[CitationItem]
    notes: list[str] = Field(default_factory=list)
    debug: DebugInfo
