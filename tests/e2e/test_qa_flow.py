from fastapi.testclient import TestClient

from app.main import app


def test_qa_ask_returns_citations() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/qa/ask",
            json={"query": "Redis 批量写入后反序列化报错怎么办", "top_k": 3, "return_context": True},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["citations"]
        assert payload["debug"]["rewritten_query"]


def test_switch_index_then_qa_still_works() -> None:
    with TestClient(app) as client:
        rebuild_response = client.post("/api/v1/admin/rebuild-index", params={"version": "v-e2e"})
        assert rebuild_response.status_code == 200

        switch_response = client.post("/api/v1/admin/index/switch", params={"version": "v-e2e"})
        assert switch_response.status_code == 200

        qa_response = client.post(
            "/api/v1/qa/ask",
            json={"query": "FastAPI upload multipart validation issue", "top_k": 3, "return_context": False},
        )
        assert qa_response.status_code == 200
        payload = qa_response.json()
        assert payload["citations"]
        assert payload["debug"]["retrieved_doc_ids"]
