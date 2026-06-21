from __future__ import annotations

from hashlib import sha256

from app.models.document import Document


def build_document_hash(document: Document) -> str:
    payload = "\n".join(
        [
            document.doc_id,
            document.title,
            document.content,
            ",".join(document.tags),
            document.source_url,
            document.language,
            str(document.score),
            str(document.is_accepted),
        ]
    )
    return sha256(payload.encode("utf-8")).hexdigest()
