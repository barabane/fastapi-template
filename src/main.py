from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import auth_router
from src.databases import redis_connection


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await redis_connection.aclose()


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router)
