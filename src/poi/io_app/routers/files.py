from fastapi import APIRouter, Query

from poi.io_app.services import storage

router = APIRouter(prefix="/files", tags=["io"])


@router.post("")
def write(kb: int = Query(256, ge=1, le=16_384)):
    return {"file": storage.write_file(kb), "size_kb": kb}


@router.get("/random")
def read_random():
    return storage.read_random_file()


@router.get("/count-lines")
def count_lines():
    return storage.count_lines()
