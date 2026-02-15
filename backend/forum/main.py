import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from forum.api import api_router
from forum.auth import utils
from forum.database.core import sessionlocal
from forum.cache.core import get_cache_pool

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting Forum API")

    app.state.cache = redis.Redis(connection_pool=get_cache_pool())
    await utils.init_roles(sessionlocal())

    # before
    yield
    # after

    await app.state.cache.close()
    log.info("Forum API stopped")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
