from poi.common.app_factory import create_app
from poi.cpu_app.routers import compute

app = create_app("cpu-bound", [compute.router])
