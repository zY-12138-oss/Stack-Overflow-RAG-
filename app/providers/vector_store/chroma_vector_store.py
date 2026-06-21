from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from app.models.document import Document
from app.providers.vector_store.base import VectorStore


class ChromaVectorStore(VectorStore):
    supports_incremental = True

    def __init__(self, persist_path: str, collection_name: str) -> None:
        Path(persist_path).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=persist_path)
        self._collection_name = collection_name
        self._collection: Collection = self._client.get_or_create_collection(name=collection_name)
        self._documents: dict[str, Document] = {}

    def build(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        self._documents = {document.doc_id: document for document in documents}
        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(name=self._collection_name)

        ids = [document.doc_id for document in documents]
        metadatas = [
            {
                "question_id": document.question_id,
                "answer_id": document.answer_id or -1,
                "doc_type": document.doc_type,
                "title": document.title,
                "score": document.score,
                "is_accepted": document.is_accepted,
                "source_url": document.source_url,
                "language": document.language,
                "tags": ",".join(document.tags),
            }
            for document in documents
        ]
        payloads = [document.content for document in documents]

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=payloads,
        )

    def upsert_documents(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        if not documents:
            return

        self._documents.update({document.doc_id: document for document in documents})
        self._collection.upsert(
            ids=[document.doc_id for document in documents],
            embeddings=embeddings,
            metadatas=[
                {
                    "question_id": document.question_id,
                    "answer_id": document.answer_id or -1,
                    "doc_type": document.doc_type,
                    "title": document.title,
                    "score": document.score,
                    "is_accepted": document.is_accepted,
                    "source_url": document.source_url,
                    "language": document.language,
                    "tags": ",".join(document.tags),
                }
                for document in documents
            ],
            documents=[document.content for document in documents],
        )

    def delete_documents(self, doc_ids: list[str]) -> None:
        if not doc_ids:
            return
        self._collection.delete(ids=doc_ids)
        for doc_id in doc_ids:
            self._documents.pop(doc_id, None)

    def search_by_vector(self, query_embedding: list[float], top_k: int) -> list[tuple[Document, float]]:
        result = self._collection.query(query_embeddings=[query_embedding], n_results=top_k)
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]

        scored: list[tuple[Document, float]] = []
        for doc_id, distance in zip(ids, distances, strict=False):
            document = self._documents.get(doc_id)
            if document is None:
                continue
            score = 1.0 / (1.0 + float(distance))
            scored.append((document, score))
        return scored
