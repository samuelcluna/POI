from contextlib import asynccontextmanager

from poi.common.app_factory import create_app
from poi.io_app.routers import files, records
from poi.io_app.services import records as records_service
from poi.io_app.services import storage


@asynccontextmanager
async def lifespan(app):
    storage.seed()
    records_service.seed()
    yield


app = create_app("io-bound", [files.router, records.router], lifespan=lifespan)
