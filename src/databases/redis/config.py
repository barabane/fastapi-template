from pydantic import computed_field
from pydantic_settings import BaseSettings

from src.config import config


class RedisConfig(BaseSettings):
    port: int
    host: str
    db: int = 0

    @computed_field
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"

redis_config = RedisConfig(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT
)