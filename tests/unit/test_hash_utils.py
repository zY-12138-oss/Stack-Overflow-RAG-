from app.models.document import Document
from app.utils.hash_utils import build_document_hash


def test_build_document_hash_changes_with_content() -> None:
    first = Document(
        doc_id="doc-1",
        question_id=1,
        title="Title",
        content="A",
        tags=["redis"],
        source_url="https://example.com",
    )
    second = Document(
        doc_id="doc-1",
        question_id=1,
        title="Title",
        content="B",
        tags=["redis"],
        source_url="https://example.com",
    )

    assert build_document_hash(first) != build_document_hash(second)
