import os
from pathlib import Path


def env_int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


def data_dir() -> Path:
    return Path(os.environ.get("DATA_DIR", "data"))
