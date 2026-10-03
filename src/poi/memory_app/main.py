from poi.common.app_factory import create_app
from poi.memory_app.routers import alloc, cache, dataset

app = create_app("memory-bound", [alloc.router, dataset.router, cache.router])
