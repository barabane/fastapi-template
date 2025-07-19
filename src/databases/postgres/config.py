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
    host=config.DB_HOST,
    port=config.DB_PORT,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    db_name=config.DB_NAME
)