from app.models.document import Document
from app.services.rerank_service import RerankService


def test_rerank_uses_preprocess_signals() -> None:
    service = RerankService()
    document = Document(
        doc_id="doc-1",
        question_id=1,
        title="Redis deserialization error in TValue",
        content="Check serializer compatibility in redis bulk write scenario with v8 client.",
        tags=["redis", ".net"],
        score=10,
        is_accepted=True,
        source_url="https://stackoverflow.com/questions/1",
    )

    ranked = service.rerank(
        query="Redis 批量写入后反序列化报错怎么办",
        results=[{"document": document, "score": 0.4, "routes": ["rewrite_to_en", "keyword"]}],
        preprocess_result={
            "keywords": ["Redis", "serializer", "bulk", "TValue"],
            "error_terms": ["error", "deserialization"],
            "versions": ["v8"],
        },
    )

    assert ranked
    assert ranked[0]["score"] > 0.4


def test_rerank_prefers_same_task_over_same_framework_only() -> None:
    service = RerankService()
    upload_doc = Document(
        doc_id="doc-upload",
        question_id=1,
        title="FastAPI file upload validation issue",
        content="Use UploadFile, File and multipart/form-data correctly to avoid validation errors.",
        tags=["python", "fastapi", "validation"],
        score=2,
        source_url="https://stackoverflow.com/questions/upload",
    )
    framework_only_doc = Document(
        doc_id="doc-msal",
        question_id=2,
        title="MSAL Package for FastAPI",
        content="FastAPI token validation with Azure AD and MSAL.",
        tags=["python", "fastapi", "msal"],
        score=2,
        source_url="https://stackoverflow.com/questions/msal",
    )

    ranked = service.rerank(
        query="FastAPI 文件上传校验失败怎么办",
        results=[
            {"document": framework_only_doc, "score": 0.72, "routes": ["rewrite_to_en"]},
            {"document": upload_doc, "score": 0.68, "routes": ["rewrite_to_en", "keyword"]},
        ],
        preprocess_result={
            "keywords": ["FastAPI", "upload", "validation", "multipart", "UploadFile"],
            "error_terms": ["validation"],
            "versions": [],
        },
    )

    assert ranked[0]["document"].doc_id == "doc-upload"
