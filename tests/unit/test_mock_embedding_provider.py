from app.providers.embedding.mock_embedding_provider import MockEmbeddingProvider


def test_mock_embedding_provider_returns_fixed_dimension() -> None:
    provider = MockEmbeddingProvider()

    left = provider.embed("short text")
    right = provider.embed("a much longer text with more tokens for testing")

    assert len(left) == provider.vector_size
    assert len(right) == provider.vector_size
