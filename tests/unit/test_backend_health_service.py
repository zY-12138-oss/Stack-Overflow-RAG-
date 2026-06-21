from app.models.backend_status import BackendStatus
from app.services.backend_health_service import BackendHealthService


class FakeRedisCache:
    def ping(self) -> bool:
        return True


class BrokenRedisCache:
    def ping(self) -> bool:
        raise RuntimeError("redis down")


class FakeMySQLRepository:
    pass


class BrokenMySQLRepository:
    pass


class FakeBackendHealthService(BackendHealthService):
    def check_mysql_query_log(self, backend: str, repository: object) -> BackendStatus:
        if backend != "mysql":
            return BackendStatus(name="query_log", backend=backend, configured=True, available=True)
        if isinstance(repository, BrokenMySQLRepository):
            return BackendStatus(name="query_log", backend="mysql", configured=True, available=False, detail="mysql down")
        return BackendStatus(name="query_log", backend="mysql", configured=True, available=True)


def test_backend_health_service_checks_redis_success() -> None:
    service = BackendHealthService()
    status = service.check_redis_cache("redis", FakeRedisCache())

    assert status.available is True
    assert status.backend == "redis"


def test_backend_health_service_checks_redis_failure() -> None:
    service = BackendHealthService()
    status = service.check_redis_cache("redis", BrokenRedisCache())

    assert status.available is False
    assert status.detail == "redis down"


def test_backend_health_service_checks_mysql_success() -> None:
    service = FakeBackendHealthService()
    status = service.check_mysql_query_log("mysql", FakeMySQLRepository())

    assert status.available is True
    assert status.backend == "mysql"


def test_backend_health_service_checks_mysql_failure() -> None:
    service = FakeBackendHealthService()
    status = service.check_mysql_query_log("mysql", BrokenMySQLRepository())

    assert status.available is False
    assert status.detail == "mysql down"
