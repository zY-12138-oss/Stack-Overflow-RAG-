from app.services.metrics_service import MetricsService


def test_metrics_service_records_request_flow() -> None:
    service = MetricsService()

    service.record_request()
    service.record_cache_miss()
    service.record_success(120)

    snapshot = service.snapshot()
    assert snapshot["total_requests"] == 1
    assert snapshot["cache_misses"] == 1
    assert snapshot["qa_successes"] == 1
    assert snapshot["average_latency_ms"] == 120.0


def test_metrics_service_records_failures() -> None:
    service = MetricsService()

    service.record_request()
    service.record_failure()

    snapshot = service.snapshot()
    assert snapshot["total_requests"] == 1
    assert snapshot["qa_failures"] == 1


def test_metrics_service_persists_to_local_file(tmp_path) -> None:
    metrics_file = tmp_path / "runtime_metrics.json"
    service = MetricsService(storage_path=metrics_file)

    service.record_request()
    service.record_cache_hit()
    service.record_success(88)

    reloaded = MetricsService(storage_path=metrics_file)
    snapshot = reloaded.snapshot()
    assert snapshot["total_requests"] == 1
    assert snapshot["cache_hits"] == 1
    assert snapshot["qa_successes"] == 1
    assert snapshot["average_latency_ms"] == 88.0


def test_metrics_service_clear_resets_and_removes_file(tmp_path) -> None:
    metrics_file = tmp_path / "runtime_metrics.json"
    service = MetricsService(storage_path=metrics_file)
    service.record_request()
    service.record_success(50)

    result = service.clear()

    assert result["status"] == "cleared"
    assert service.snapshot()["total_requests"] == 0
    assert metrics_file.exists() is False
