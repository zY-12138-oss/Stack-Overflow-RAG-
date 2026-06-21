from app.providers.embedding.local_hash_embedding_provider import LocalHashEmbeddingProvider


def test_local_hash_embedding_provider_returns_fixed_dimension() -> None:
    provider = LocalHashEmbeddingProvider(vector_size=128)

    left = provider.embed("redis deserialize error")
    right = provider.embed("redis 批量 写入 反序列化 报错")

    assert len(left) == 128
    assert len(right) == 128


def test_local_hash_embedding_provider_is_deterministic() -> None:
    provider = LocalHashEmbeddingProvider(vector_size=64)

    first = provider.embed("same input")
    second = provider.embed("same input")

    assert first == second
