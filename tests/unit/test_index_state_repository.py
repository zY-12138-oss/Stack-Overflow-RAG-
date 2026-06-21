from app.repositories.index_state_repository import IndexStateRepository


def test_index_state_repository_persists_hashes(tmp_path) -> None:
    state_file = tmp_path / "index_state.json"
    repository = IndexStateRepository(storage_path=state_file)

    repository.save_many({"doc-1": "hash-a", "doc-2": "hash-b"}, version="v3")

    assert repository.load() == {"doc-1": "hash-a", "doc-2": "hash-b"}
