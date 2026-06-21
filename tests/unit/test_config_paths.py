from pathlib import Path

from app.core.config import settings


def test_resolve_path_uses_project_root_for_relative_paths() -> None:
    resolved = settings.resolve_path("data/local_cache/answer_cache.json")

    assert resolved.is_absolute()
    assert str(resolved).endswith(str(Path("data") / "local_cache" / "answer_cache.json"))
