from fastapi import APIRouter, HTTPException, Query

from poi.memory_app.services.cache import cache

router = APIRouter(prefix="/cache", tags=["memory"])


@router.get("/stats")
def stats():
    return cache.stats()


@router.delete("")
def clear():
    cache.clear()
    return cache.stats()


@router.put("/{key}")
def put(key: str, kb: int = Query(256, ge=1, le=65_536)):
    cache.put(key, kb * 1024)
    return {"key": key, "size_kb": kb}


@router.get("/{key}")
def get(key: str):
    value = cache.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="chave não está no cache")
    return {"key": key, "size_kb": len(value) // 1024}
