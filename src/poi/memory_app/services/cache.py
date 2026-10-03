import threading
from collections import OrderedDict

from poi.common.settings import env_int

MB = 1024 * 1024


class MemoryCache:
    def __init__(self, max_bytes: int):
        self.max_bytes = max_bytes
        self._items: OrderedDict[str, bytes] = OrderedDict()
        self._bytes = 0
        self._evictions = 0
        self._lock = threading.Lock()

    def put(self, key: str, size: int) -> None:
        value = b"x" * size
        with self._lock:
            old = self._items.pop(key, None)
            if old is not None:
                self._bytes -= len(old)
            self._items[key] = value
            self._bytes += size
            while self._bytes > self.max_bytes and len(self._items) > 1:
                _, evicted = self._items.popitem(last=False)
                self._bytes -= len(evicted)
                self._evictions += 1

    def get(self, key: str) -> bytes | None:
        with self._lock:
            value = self._items.get(key)
            if value is not None:
                self._items.move_to_end(key)
            return value

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._bytes = 0

    def stats(self) -> dict:
        with self._lock:
            return {
                "items": len(self._items),
                "used_mb": round(self._bytes / MB, 2),
                "max_mb": round(self.max_bytes / MB, 2),
                "evictions": self._evictions,
            }


cache = MemoryCache(env_int("CACHE_MAX_MB", 256) * MB)
