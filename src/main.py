from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import auth_router
from src.databases.redis import redis_connection


@asynccontextmanager
async def lifespan(_: FastAPI):
    await redis_connection.connect()
    yield
    await redis_connection.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router)
