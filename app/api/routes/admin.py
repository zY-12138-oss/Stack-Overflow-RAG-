from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.providers.vector_store.factory import build_vector_store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/rebuild-index")
def rebuild_index(request: Request, version: str | None = None) -> dict[str, str | int]:
    repository = request.app.state.document_repository
    retrieval_service = request.app.state.retrieval_service
    catalog_repository = request.app.state.index_catalog_repository

    target_version = version or request.app.state.active_index_version
    catalog_repository.update_status(target_version, "building")

    try:
        docs = repository.load_seed_documents(force_reload=True)
        retrieval_service.build_index(docs)
        catalog_repository.update_status(
            target_version,
            "ready",
            {"documents": len(docs)},
        )
        return {"status": "rebuilt", "documents": len(docs), "version": target_version}
    except Exception as exc:
        catalog_repository.update_status(
            target_version,
            "failed",
            {"error": str(exc)},
        )
        raise


@router.get("/index/versions")
def list_index_versions(request: Request) -> dict[str, object]:
    catalog_repository = request.app.state.index_catalog_repository
    data = catalog_repository.list_versions()
    return {
        "active_version": request.app.state.active_index_version,
        "versions": data.get("versions", {}),
    }


@router.post("/index/switch")
def switch_index(request: Request, version: str) -> dict[str, str]:
    catalog_repository = request.app.state.index_catalog_repository
    catalog = catalog_repository.list_versions()
    versions = catalog.get("versions", {})
    if version not in versions:
        raise HTTPException(status_code=404, detail=f"索引版本不存在：{version}")

    target_version = catalog_repository.get_version(version)
    if not target_version:
        raise HTTPException(status_code=404, detail=f"索引版本不存在：{version}")
    if target_version.get("status") != "ready":
        raise HTTPException(status_code=409, detail=f"索引版本未就绪：{version}")

    previous_version = request.app.state.active_index_version
    previous_store = request.app.state.retrieval_service.vector_store

    try:
        request.app.state.retrieval_service.vector_store = build_vector_store(version=version)
        request.app.state.active_index_version = version
        catalog_repository.set_active(version)
        return {"status": "switched", "active_index_version": version}
    except Exception as exc:
        request.app.state.retrieval_service.vector_store = previous_store
        request.app.state.active_index_version = previous_version
        catalog_repository.set_active(previous_version)
        raise HTTPException(status_code=500, detail=f"索引切换失败，已回滚：{exc}") from exc


@router.get("/runtime/status")
def runtime_status(request: Request) -> dict[str, object]:
    return {
        "phase": settings.phase_name,
        "active_index_version": request.app.state.active_index_version,
        "vector_store_provider": settings.vector_store_provider,
        "embedding_provider_mode": settings.embedding_provider_mode,
        "provider_mode": settings.provider_mode,
        "backends": getattr(request.app.state, "backend_status", {}),
    }


@router.get("/runtime/metrics")
def runtime_metrics(request: Request) -> dict[str, int | float]:
    metrics_service = request.app.state.metrics_service
    return metrics_service.snapshot()


@router.post("/runtime/metrics/clear")
def clear_runtime_metrics(request: Request) -> dict[str, object]:
    metrics_service = request.app.state.metrics_service
    return metrics_service.clear()


@router.get("/query-logs")
def list_query_logs(request: Request, limit: int = 20) -> dict[str, object]:
    repository = request.app.state.query_log_repository
    return {
        "items": [item.model_dump(mode="json") for item in repository.list_recent(limit=limit)],
        "stats": repository.stats(),
    }


@router.get("/cache/stats")
def cache_stats(request: Request) -> dict[str, int]:
    cache_service = request.app.state.cache_service
    return cache_service.stats()


@router.post("/cache/clear")
def clear_cache(request: Request) -> dict[str, object]:
    cache_service = request.app.state.cache_service
    result = cache_service.clear()
    return {"status": "cleared", **result}
