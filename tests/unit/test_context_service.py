from app.models.document import Document
from app.services.context_service import ContextService


def test_context_builds_structured_blocks() -> None:
    service = ContextService()
    ranked_results = [
        {
            "document": Document(
                doc_id="doc-1",
                question_id=1,
                title="Example",
                content="Example answer body",
                source_url="https://stackoverflow.com/questions/1",
                tags=["python"],
            ),
            "score": 0.9,
        }
    ]

    context = service.build_context(ranked_results)

    assert "[Document 1]" in context
    assert "Source:" in context
