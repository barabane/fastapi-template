from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    SECRET: str
    ALGORITHM: str

    SMTP_PASSWORD: str
    SMTP_USERNAME: str
    SMTP_HOST: str
    SMTP_PORT: int

    LOGS_LEVEL: str

    model_config = SettingsConfigDict(env_file=".env")

config = Config() #type: ignore