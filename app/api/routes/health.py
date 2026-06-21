from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request) -> dict[str, object]:
    active_version = getattr(request.app.state, "active_index_version", "unknown")
    backend_status = getattr(request.app.state, "backend_status", {})
    return {
        "status": "ok",
        "active_index_version": str(active_version),
        "backends": backend_status,
    }


@router.get("/ready")
def ready(request: Request) -> dict[str, object]:
    active_version = getattr(request.app.state, "active_index_version", "unknown")
    backend_status = getattr(request.app.state, "backend_status", {})
    overall_ready = all(item.get("available", False) or item.get("degraded_to") for item in backend_status.values())
    return {
        "status": "ready" if overall_ready else "degraded",
        "active_index_version": str(active_version),
        "backends": backend_status,
    }
