from fastapi.testclient import TestClient

from app.main import app


def test_runtime_status_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/admin/runtime/status")
        assert response.status_code == 200
        payload = response.json()
        assert "phase" in payload
        assert "active_index_version" in payload
        assert "vector_store_provider" in payload


def test_runtime_metrics_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/admin/runtime/metrics")
        assert response.status_code == 200
        payload = response.json()
        assert "total_requests" in payload
        assert "qa_successes" in payload
        assert "average_latency_ms" in payload


def test_clear_runtime_metrics_endpoint() -> None:
    with TestClient(app) as client:
        client.get("/api/v1/admin/runtime/metrics")
        response = client.post("/api/v1/admin/runtime/metrics/clear")
        assert response.status_code == 200
        assert response.json()["status"] == "cleared"


def test_index_versions_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/admin/index/versions")
        assert response.status_code == 200
        payload = response.json()
        assert "active_version" in payload
        assert "versions" in payload
        assert isinstance(payload["versions"], dict)


def test_switch_index_returns_404_for_unknown_version() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/admin/index/switch", params={"version": "not-exists"})
        assert response.status_code == 404


def test_switch_index_rejects_unready_version() -> None:
    with TestClient(app) as client:
        client.app.state.index_catalog_repository.update_status("v-building", "building")
        response = client.post("/api/v1/admin/index/switch", params={"version": "v-building"})
        assert response.status_code == 409


def test_switch_index_updates_active_version() -> None:
    with TestClient(app) as client:
        rebuild_response = client.post("/api/v1/admin/rebuild-index", params={"version": "v-switch-test"})
        assert rebuild_response.status_code == 200

        switch_response = client.post("/api/v1/admin/index/switch", params={"version": "v-switch-test"})
        assert switch_response.status_code == 200
        assert switch_response.json()["active_index_version"] == "v-switch-test"

        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200
        assert health_response.json()["active_index_version"] == "v-switch-test"


def test_rebuild_index_marks_version_ready() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/admin/rebuild-index", params={"version": "v-ready-check"})
        assert response.status_code == 200

        versions = client.get("/api/v1/admin/index/versions").json()["versions"]
        assert versions["v-ready-check"]["status"] == "ready"
