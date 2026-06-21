from app.models.backend_status import BackendStatus


def test_backend_status_to_dict() -> None:
    status = BackendStatus(
        name="cache",
        backend="redis",
        configured=True,
        available=False,
        degraded_to="local_file",
        detail="connection refused",
    )

    payload = status.to_dict()
    assert payload["name"] == "cache"
    assert payload["backend"] == "redis"
    assert payload["degraded_to"] == "local_file"
