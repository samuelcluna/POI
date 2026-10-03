from fastapi import APIRouter, HTTPException, Query

from poi.io_app.services import records as service

router = APIRouter(prefix="/records", tags=["io"])


@router.post("")
def create(size: int = Query(512, ge=1, le=65_536)):
    return {"id": service.insert("r" * size)}


@router.get("/{record_id}")
def read(record_id: int):
    record = service.get(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="registro não encontrado")
    return record
