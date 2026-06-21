import json
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import DataIngestError
from app.models.document import Document


class DocumentRepository:
    def __init__(self) -> None:
        self._cache: list[Document] | None = None

    def load_seed_documents(self, force_reload: bool = False) -> list[Document]:
        if self._cache is not None and not force_reload:
            return self._cache

        path = settings.seed_data_path_resolved
        if not path.exists():
            self._cache = self._build_fallback_documents()
            return self._cache

        documents: list[Document] = []
        try:
            with path.open("r", encoding="utf-8-sig") as handle:
                for index, line in enumerate(handle):
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    documents.append(self._from_raw_item(item, index))
        except (OSError, json.JSONDecodeError) as exc:
            raise DataIngestError(f"failed to load seed documents: {exc}") from exc

        self._cache = documents or self._build_fallback_documents()
        return self._cache

    def _from_raw_item(self, item: dict, index: int) -> Document:
        title = item.get("title", "").strip() or f"Stack Overflow Question {index}"
        question_body = item.get("question_body", "")
        answers = item.get("answers", [])
        selected_answer = answers[0]["body"] if answers else ""
        content = "\n".join(part for part in [question_body, selected_answer] if part)
        return Document(
            doc_id=f"so_{item.get('question_id', index)}_chunk_0",
            question_id=int(item.get("question_id", index)),
            answer_id=item.get("accepted_answer_id"),
            title=title,
            content=content[:4000],
            tags=item.get("tags", []),
            score=int(item.get("score", 0)),
            is_accepted=bool(item.get("accepted_answer_id")),
            source_url=item.get("link", "https://stackoverflow.com"),
        )

    def _build_fallback_documents(self) -> list[Document]:
        return [
            Document(
                doc_id="fallback_redis_deserialize",
                question_id=1,
                title="Unable to deserialize the data into TValue",
                content=(
                    "Question: Redis bulk write fails with TValue deserialization error. "
                    "Answer: verify the serializer matches the stored payload and target generic type."
                ),
                tags=["c#", ".net", "redis"],
                source_url="https://stackoverflow.com/questions/79320365",
                is_accepted=True,
                score=10,
            ),
            Document(
                doc_id="fallback_fastapi_upload",
                question_id=2,
                title="FastAPI file upload validation issue",
                content=(
                    "Question: FastAPI upload endpoint rejects multipart form. "
                    "Answer: ensure UploadFile and Form are declared correctly and content-type is multipart/form-data."
                ),
                tags=["python", "fastapi"],
                source_url="https://stackoverflow.com/questions/example-fastapi-upload",
                score=8,
            ),
        ]
