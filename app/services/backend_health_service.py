from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.backend_status import BackendStatus
from app.repositories.mysql_query_log_repository import MySQLQueryLogRepository
from app.services.redis_cache_service import RedisCacheService


class BackendHealthService:
    def check_redis_cache(self, backend: str, cache_service: object) -> BackendStatus:
        if backend != "redis":
            return BackendStatus(name="cache", backend=backend, configured=True, available=True)
        try:
            assert isinstance(cache_service, RedisCacheService)
            cache_service.ping()
            return BackendStatus(name="cache", backend="redis", configured=True, available=True)
        except Exception as exc:
            return BackendStatus(name="cache", backend="redis", configured=True, available=False, detail=str(exc))

    def check_mysql_query_log(self, backend: str, repository: object) -> BackendStatus:
        if backend != "mysql":
            return BackendStatus(name="query_log", backend=backend, configured=True, available=True)
        try:
            assert isinstance(repository, MySQLQueryLogRepository)
            with Session(repository.engine) as session:
                session.execute(text("SELECT 1"))
            return BackendStatus(name="query_log", backend="mysql", configured=True, available=True)
        except SQLAlchemyError as exc:
            return BackendStatus(name="query_log", backend="mysql", configured=True, available=False, detail=str(exc))
        except Exception as exc:
            return BackendStatus(name="query_log", backend="mysql", configured=True, available=False, detail=str(exc))
