from app.repositories.index_catalog_repository import IndexCatalogRepository


def test_index_catalog_repository_sets_active_version(tmp_path) -> None:
    catalog_file = tmp_path / "index_catalog.json"
    repository = IndexCatalogRepository(storage_path=catalog_file)

    repository.upsert_version("v1", {"documents": 10})
    repository.upsert_version("v2", {"documents": 20})
    payload = repository.set_active("v2")

    assert payload["active_version"] == "v2"
    assert payload["versions"]["v1"]["documents"] == 10
    assert payload["versions"]["v2"]["documents"] == 20


def test_index_catalog_repository_initializes_active_version(tmp_path) -> None:
    catalog_file = tmp_path / "index_catalog.json"
    repository = IndexCatalogRepository(storage_path=catalog_file)

    payload = repository.upsert_version("v1", {"documents": 5})

    assert payload["active_version"] == "v1"
    assert payload["versions"]["v1"]["documents"] == 5


def test_index_catalog_repository_updates_status(tmp_path) -> None:
    catalog_file = tmp_path / "index_catalog.json"
    repository = IndexCatalogRepository(storage_path=catalog_file)

    repository.upsert_version("v1")
    payload = repository.update_status("v1", "building", {"documents": 3})

    assert payload["versions"]["v1"]["status"] == "building"
    assert payload["versions"]["v1"]["documents"] == 3
