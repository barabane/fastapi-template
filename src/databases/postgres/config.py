from pydantic_settings import BaseSettings

from src.config import config


class PostgresConfig(BaseSettings):
    driver: str
    host: str
    port: int
    user: str
    password: str
    db_name: str

    @property
    def url(self) -> str:
        return f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


postgres_config = PostgresConfig(
    driver="asyncpg",
    host=config.POSTGRES_HOST,
    port=config.POSTGRES_PORT,
    user=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
    db_name=config.POSTGRES_DB,
)
