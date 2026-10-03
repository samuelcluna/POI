from fastapi.testclient import TestClient

from poi.cpu_app.main import app

client = TestClient(app)


def test_health_and_metrics():
    assert client.get("/health").json()["profile"] == "cpu-bound"
    assert client.get("/metrics").json()["process"]["rss_mb"] > 0


def test_primes():
    assert client.get("/primes", params={"limit": 100}).json()["primes"] == 25


def test_sort():
    body = client.get("/sort", params={"n": 1000}).json()
    assert body["min"] <= body["median"] <= body["max"]


def test_matrix():
    assert client.get("/matrix", params={"size": 5}).json()["trace"] > 0


def test_hash():
    assert len(client.get("/hash", params={"iterations": 10}).json()["digest"]) == 64


def test_limits_are_enforced():
    assert client.get("/primes", params={"limit": 10**9}).status_code == 422
    assert "x-process-time" in client.get("/health").headers
