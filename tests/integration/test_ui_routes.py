from fastapi.testclient import TestClient

from app.main import app


def test_root_ui_page_returns_html() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "/api/v1/qa/ask" in response.text


def test_admin_ui_page_returns_html() -> None:
    with TestClient(app) as client:
        response = client.get("/admin-ui")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "/api/v1/admin/runtime/status" in response.text
