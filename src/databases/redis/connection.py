from redis import asyncio as aioredis

from .config import redis_config

connection: aioredis.Redis = aioredis.from_url(**redis_config.model_dump())
