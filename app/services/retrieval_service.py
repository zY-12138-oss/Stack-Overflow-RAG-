from app.models.document import Document
from app.providers.embedding.base import EmbeddingProvider
from app.providers.vector_store.base import VectorStore
from app.repositories.document_repository import DocumentRepository
from app.repositories.index_state_repository import IndexStateRepository
from app.utils.hash_utils import build_document_hash


class RetrievalService:
    def __init__(
        self,
        repository: DocumentRepository,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
        index_state_repository: IndexStateRepository | None = None,
    ) -> None:
        self.repository = repository
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.index_state_repository = index_state_repository

    def build_index(self, documents: list[Document]) -> None:
        if self.index_state_repository is not None and self.vector_store.supports_incremental:
            self._build_index_incrementally(documents)
            return

        texts = [
            f"{document.title}\n{document.content}\n{' '.join(document.tags)}"
            for document in documents
        ]
        embeddings = self.embedding_provider.embed_batch(texts)
        self.vector_store.build(documents, embeddings)

        if self.index_state_repository is not None:
            self.index_state_repository.save_many(
                {document.doc_id: build_document_hash(document) for document in documents}
            )

    def retrieve(self, query: str, top_k: int) -> list[dict[str, object]]:
        query_embedding = self.embedding_provider.embed(query)
        try:
            results = self.vector_store.search_by_vector(query_embedding, top_k)
        except Exception as exc:
            if not self._is_dimension_mismatch_error(exc):
                raise
            documents = self.repository.load_seed_documents(force_reload=True)
            self._force_full_rebuild(documents)
            results = self.vector_store.search_by_vector(query_embedding, top_k)
        return [
            {"document": document, "score": score, "route": "vector", "routes": ["vector"]}
            for document, score in results
        ]

    def retrieve_dual(
        self,
        primary_query: str,
        secondary_query: str | None,
        top_k: int,
        keyword_candidates: list[dict[str, object]] | None = None,
    ) -> dict[str, list[dict[str, object]]]:
        route_results: dict[str, list[dict[str, object]]] = {
            "rewrite_to_en": self.retrieve(primary_query, top_k),
        }
        if secondary_query and secondary_query.strip():
            route_results["zh_query"] = self.retrieve(secondary_query, top_k)
        if keyword_candidates:
            route_results["keyword"] = keyword_candidates
        return route_results

    def merge_results(
        self,
        route_results: dict[str, list[dict[str, object]]],
        top_k: int,
    ) -> list[dict[str, object]]:
        merged: dict[str, dict[str, object]] = {}
        for route_name, results in route_results.items():
            for item in results:
                document = item["document"]
                score = float(item["score"])
                existing = merged.get(document.doc_id)
                if existing is None or score > float(existing["score"]):
                    previous_routes = set(existing.get("routes", [])) if existing else set()
                    merged[document.doc_id] = {
                        "document": document,
                        "score": score,
                        "route": route_name,
                        "routes": sorted(previous_routes | {route_name}),
                    }
                else:
                    existing_routes = set(existing.get("routes", []))
                    existing_routes.add(route_name)
                    existing["routes"] = sorted(existing_routes)
        ranked = sorted(merged.values(), key=lambda item: float(item["score"]), reverse=True)
        return ranked[:top_k]

    def retrieve_by_keywords(
        self,
        keywords: list[str],
        error_terms: list[str],
        versions: list[str],
        top_k: int,
    ) -> list[dict[str, object]]:
        scored: list[dict[str, object]] = []
        all_documents = self.repository.load_seed_documents()
        if not any([keywords, error_terms, versions]):
            return []

        for document in all_documents:
            title = document.title.lower()
            content = document.content.lower()
            tags = [tag.lower() for tag in document.tags]

            keyword_hits = sum(1 for term in keywords if term.lower() in title or term.lower() in content)
            error_hits = sum(1 for term in error_terms if term.lower() in content or term.lower() in title)
            version_hits = sum(1 for term in versions if term.lower() in content or term.lower() in title)
            tag_hits = sum(1 for term in keywords if term.lower() in tags)

            score = (
                keyword_hits * 0.12
                + error_hits * 0.18
                + version_hits * 0.08
                + tag_hits * 0.15
            )
            if score <= 0:
                continue
            scored.append(
                {
                    "document": document,
                    "score": score,
                    "route": "keyword",
                    "routes": ["keyword"],
                }
            )

        scored.sort(key=lambda item: float(item["score"]), reverse=True)
        return scored[:top_k]

    def _build_index_incrementally(self, documents: list[Document]) -> None:
        assert self.index_state_repository is not None

        previous_state = self.index_state_repository.load()
        current_hashes = {document.doc_id: build_document_hash(document) for document in documents}

        changed_documents = [
            document
            for document in documents
            if previous_state.get(document.doc_id) != current_hashes[document.doc_id]
        ]
        deleted_doc_ids = [doc_id for doc_id in previous_state if doc_id not in current_hashes]

        if changed_documents:
            texts = [
                f"{document.title}\n{document.content}\n{' '.join(document.tags)}"
                for document in changed_documents
            ]
            embeddings = self.embedding_provider.embed_batch(texts)
            try:
                self.vector_store.upsert_documents(changed_documents, embeddings)
            except Exception as exc:
                if self._is_dimension_mismatch_error(exc):
                    self._rebuild_index_from_scratch(documents, current_hashes)
                    return
                raise

        if deleted_doc_ids:
            try:
                self.vector_store.delete_documents(deleted_doc_ids)
            except Exception as exc:
                if self._is_dimension_mismatch_error(exc):
                    self._rebuild_index_from_scratch(documents, current_hashes)
                    return
                raise

        self.index_state_repository.save_many(current_hashes)

    def _rebuild_index_from_scratch(
        self,
        documents: list[Document],
        current_hashes: dict[str, str],
    ) -> None:
        texts = [
            f"{document.title}\n{document.content}\n{' '.join(document.tags)}"
            for document in documents
        ]
        embeddings = self.embedding_provider.embed_batch(texts)
        self.vector_store.build(documents, embeddings)
        self.index_state_repository.save_many(current_hashes)

    def _force_full_rebuild(self, documents: list[Document]) -> None:
        texts = [
            f"{document.title}\n{document.content}\n{' '.join(document.tags)}"
            for document in documents
        ]
        embeddings = self.embedding_provider.embed_batch(texts)
        self.vector_store.build(documents, embeddings)
        if self.index_state_repository is not None:
            self.index_state_repository.save_many(
                {document.doc_id: build_document_hash(document) for document in documents}
            )

    @staticmethod
    def _is_dimension_mismatch_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return "dimension" in message and ("expecting embedding" in message or "got " in message)
