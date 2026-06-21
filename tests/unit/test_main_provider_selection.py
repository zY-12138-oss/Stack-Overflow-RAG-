from app.main import build_embedding_provider, settings
from app.providers.embedding.local_hash_embedding_provider import LocalHashEmbeddingProvider


def test_build_embedding_provider_prefers_local_hash_when_llm_is_cloud() -> None:
    original_provider_mode = settings.provider_mode
    original_embedding_provider_mode = settings.embedding_provider_mode
    original_dimensions = settings.local_embedding_dimensions
    try:
        settings.provider_mode = "openai_compatible"
        settings.embedding_provider_mode = "local_hash"
        settings.local_embedding_dimensions = 128

        provider = build_embedding_provider()

        assert isinstance(provider, LocalHashEmbeddingProvider)
        assert provider.vector_size == 128
    finally:
        settings.provider_mode = original_provider_mode
        settings.embedding_provider_mode = original_embedding_provider_mode
        settings.local_embedding_dimensions = original_dimensions
