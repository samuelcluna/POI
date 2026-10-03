from fastapi import APIRouter, Query

from poi.memory_app.services import alloc as service

router = APIRouter(tags=["memory"])


@router.get("/alloc")
def alloc(mb: int = Query(64, ge=1, le=512), hold_ms: int = Query(250, ge=0, le=10_000)):
    allocated = service.allocate_and_hold(mb, hold_ms)
    return {"allocated_bytes": allocated, "hold_ms": hold_ms}
