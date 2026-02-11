import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from forum.api import api_router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting Forum API")

    # before
    yield
    # after

    log.info("Forum API stopped")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
