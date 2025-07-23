from redis import asyncio as aioredis

from .config import RedisConfig, redis_config


class RedisConnection:
    def __init__(self, config: RedisConfig):
        self._config: RedisConfig = config
        self._connection: aioredis.Redis | None = None

    async def connect(self) -> aioredis.Redis:
        self._connection = await aioredis.from_url(**self._config.model_dump())
        return self._connection

    async def disconnect(self):
        if self._connection:
            await self._connection.aclose()

    @property
    def rc(self) -> aioredis.Redis:
        if not self._connection:
            raise ValueError("Redis not connected")

        return self._connection


redis_connection = RedisConnection(redis_config)
