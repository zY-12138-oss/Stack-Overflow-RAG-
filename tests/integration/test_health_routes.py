from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "active_index_version" in payload
    assert "backends" in payload


def test_ready_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ready", "degraded"}
    assert "active_index_version" in payload
    assert "backends" in payload
