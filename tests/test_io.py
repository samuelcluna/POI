import pytest
from fastapi.testclient import TestClient

from poi.io_app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("IO_SEED_FILES", "2")
    monkeypatch.setenv("IO_SEED_FILE_KB", "8")
    monkeypatch.setenv("IO_LINES_MB", "1")
    monkeypatch.setenv("IO_SEED_RECORDS", "5")
    with TestClient(app) as c:
        yield c


def test_write_file(client, tmp_path):
    body = client.post("/files", params={"kb": 4}).json()
    assert (tmp_path / "uploads" / body["file"]).stat().st_size == 4 * 1024


def test_read_random(client):
    assert client.get("/files/random").json()["bytes"] == 8 * 1024


def test_count_lines(client):
    body = client.get("/files/count-lines").json()
    assert body["lines"] > 0
    assert body["lines"] == body["bytes"] // 74


def test_records(client):
    assert client.get("/records/1").status_code == 200
    new_id = client.post("/records", params={"size": 10}).json()["id"]
    assert new_id == 6
    assert client.get(f"/records/{new_id}").json()["payload"] == "r" * 10
    assert client.get("/records/9999").status_code == 404
