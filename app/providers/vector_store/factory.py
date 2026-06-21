from app.core.config import settings
from app.providers.vector_store.base import VectorStore
from app.providers.vector_store.in_memory_vector_store import InMemoryVectorStore


def build_vector_store(version: str | None = None) -> VectorStore:
    if settings.vector_store_provider == "chroma":
        from app.providers.vector_store.chroma_vector_store import ChromaVectorStore

        active_version = version or settings.active_index_version
        collection_name = f"{settings.chroma_collection_name}_{active_version}"
        return ChromaVectorStore(
            persist_path=str(settings.chroma_persist_path_resolved),
            collection_name=collection_name,
        )
    return InMemoryVectorStore()
