"""Sobe uma das aplicações: python -m poi.run <cpu|memory|io>"""
import os
import sys

import uvicorn

# app -> (alvo ASGI, porta padrão, workers fixos). memory é stateful, então 1 worker.
APPS = {
    "cpu": ("poi.cpu_app.main:app", 8001, None),
    "memory": ("poi.memory_app.main:app", 8002, 1),
    "io": ("poi.io_app.main:app", 8003, None),
}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in APPS:
        sys.exit(f"uso: python -m poi.run <{'|'.join(APPS)}>")
    target, port, fixed_workers = APPS[sys.argv[1]]
    # um worker por vCPU, por causa do GIL
    workers = int(os.environ.get("WORKERS") or fixed_workers or os.cpu_count() or 1)
    uvicorn.run(
        target,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", port)),
        workers=workers,
        access_log=False,
    )


if __name__ == "__main__":
    main()
