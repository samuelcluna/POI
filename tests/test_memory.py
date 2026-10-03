from fastapi.testclient import TestClient

from poi.memory_app.main import app
from poi.memory_app.services.cache import MemoryCache

client = TestClient(app)


def test_alloc():
    body = client.get("/alloc", params={"mb": 2, "hold_ms": 0}).json()
    assert body["allocated_bytes"] == 2 * 1024 * 1024


def test_dataset_aggregate():
    body = client.get("/dataset/aggregate", params={"rows": 800}).json()
    assert sum(c["count"] for c in body["categories"].values()) == 800


def test_cache_roundtrip():
    client.delete("/cache")
    assert client.get("/cache/k1").status_code == 404
    assert client.put("/cache/k1", params={"kb": 4}).status_code == 200
    assert client.get("/cache/k1").json()["size_kb"] == 4
    assert client.get("/cache/stats").json()["items"] == 1
    assert client.delete("/cache").json()["items"] == 0


def test_cache_evicts_least_recently_used():
    cache = MemoryCache(max_bytes=3000)
    cache.put("a", 1000)
    cache.put("b", 1000)
    cache.put("c", 1000)
    cache.get("a")
    cache.put("d", 1000)
    assert cache.get("b") is None
    assert cache.get("a") is not None
    assert cache.stats()["evictions"] == 1
