from fastapi import APIRouter, Query

from poi.memory_app.services import dataset as service

router = APIRouter(prefix="/dataset", tags=["memory"])


@router.get("/aggregate")
def aggregate(rows: int = Query(50_000, ge=1, le=1_000_000), seed: int = 42):
    return {"rows": rows, "categories": service.load_and_aggregate(rows, seed)}
