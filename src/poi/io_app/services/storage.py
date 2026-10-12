import fcntl
import os
import random
from pathlib import Path

from poi.common.settings import data_dir, env_int

KB = 1024
CHUNK = 1024 * KB
LINE = b"linha de exemplo para o endpoint de contagem de linhas do perfil IO-bound\n"


def seed_dir() -> Path:
    return data_dir() / "seed"


def upload_dir() -> Path:
    return data_dir() / "uploads"


def lines_file() -> Path:
    return data_dir() / "lines.txt"


def _write_synced(path: Path, data: bytes, repeat: int = 1) -> None:
    with open(path, "wb") as f:
        for _ in range(repeat):
            f.write(data)
        f.flush()
        os.fsync(f.fileno())


def _drop_page_cache(fd: int) -> None:
    if hasattr(os, "posix_fadvise"):
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)


def seed() -> None:
    seed_dir().mkdir(parents=True, exist_ok=True)
    upload_dir().mkdir(parents=True, exist_ok=True)
    file_bytes = env_int("IO_SEED_FILE_KB", 1024) * KB
    lines_repeat = env_int("IO_LINES_MB", 16) * 1024 * KB // len(LINE)

    with open(data_dir() / ".seed.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for i in range(env_int("IO_SEED_FILES", 32)):
            path = seed_dir() / f"{i:04d}.bin"
            if not path.exists() or path.stat().st_size != file_bytes:
                _write_synced(path, os.urandom(file_bytes))
        if not lines_file().exists() or lines_file().stat().st_size != lines_repeat * len(LINE):
            _write_synced(lines_file(), LINE, repeat=lines_repeat)


def write_file(kb: int) -> str:
    slot = random.randrange(env_int("IO_UPLOAD_SLOTS", 200))
    path = upload_dir() / f"{slot:04d}.bin"
    _write_synced(path, b"x" * KB, repeat=kb)
    return path.name


def read_random_file() -> dict:
    path = random.choice(sorted(seed_dir().iterdir()))
    total = 0
    with open(path, "rb", buffering=0) as f:
        _drop_page_cache(f.fileno())
        while chunk := f.read(CHUNK):
            total += len(chunk)
    return {"file": path.name, "bytes": total}


def count_lines() -> dict:
    lines = total = 0
    with open(lines_file(), "rb", buffering=0) as f:
        _drop_page_cache(f.fileno())
        while chunk := f.read(CHUNK):
            lines += chunk.count(b"\n")
            total += len(chunk)
    return {"lines": lines, "bytes": total}
