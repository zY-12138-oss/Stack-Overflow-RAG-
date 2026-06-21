from pydantic import BaseModel, Field


class Document(BaseModel):
    doc_id: str
    question_id: int
    answer_id: int | None = None
    doc_type: str = "question_answer_unit"
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    score: int = 0
    is_accepted: bool = False
    source_url: str
    language: str = "en"
