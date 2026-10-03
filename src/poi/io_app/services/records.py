import sqlite3
from contextlib import closing

from poi.common.settings import data_dir, env_int


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(data_dir() / "records.db", timeout=30)
    # commit só retorna depois do fsync
    conn.execute("PRAGMA synchronous=FULL")
    return conn


def seed() -> None:
    data_dir().mkdir(parents=True, exist_ok=True)
    with closing(_connect()) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT NOT NULL)"
        )
        missing = env_int("IO_SEED_RECORDS", 1000) - conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        if missing > 0:
            conn.executemany("INSERT INTO records (payload) VALUES (?)", [("seed" * 64,)] * missing)
        conn.commit()


def insert(payload: str) -> int:
    with closing(_connect()) as conn:
        cursor = conn.execute("INSERT INTO records (payload) VALUES (?)", (payload,))
        conn.commit()
        return cursor.lastrowid


def get(record_id: int) -> dict | None:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT id, payload FROM records WHERE id = ?", (record_id,)).fetchone()
    return {"id": row[0], "payload": row[1]} if row else None
