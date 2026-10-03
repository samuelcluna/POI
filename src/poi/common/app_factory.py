import os
import time

import psutil
from fastapi import APIRouter, FastAPI, Request

MB = 1024 * 1024


def _base_router(profile: str) -> APIRouter:
    router = APIRouter(tags=["infra"])
    process = psutil.Process()

    @router.get("/health")
    def health():
        return {"status": "ok", "profile": profile, "pid": os.getpid()}

    @router.get("/metrics")
    def metrics():
        mem = psutil.virtual_memory()
        cpu = process.cpu_times()
        return {
            "profile": profile,
            "pid": os.getpid(),
            "process": {
                "rss_mb": round(process.memory_info().rss / MB, 1),
                "cpu_user_s": cpu.user,
                "cpu_system_s": cpu.system,
                "threads": process.num_threads(),
            },
            "system": {
                "cpus": psutil.cpu_count(),
                "load1": os.getloadavg()[0],
                "mem_total_mb": round(mem.total / MB, 1),
                "mem_available_mb": round(mem.available / MB, 1),
                "swap_used_mb": round(psutil.swap_memory().used / MB, 1),
            },
        }

    return router


def create_app(profile: str, routers: list[APIRouter], lifespan=None) -> FastAPI:
    app = FastAPI(title=f"POI - {profile}", lifespan=lifespan)

    @app.middleware("http")
    async def process_time(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
        return response

    app.include_router(_base_router(profile))
    for router in routers:
        app.include_router(router)
    return app
