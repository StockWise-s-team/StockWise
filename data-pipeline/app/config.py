import os
from pathlib import Path

from pydantic_settings import BaseSettings


def _root_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "stockwise"
    POSTGRES_USER: str = "stockwise"
    POSTGRES_PASSWORD: str = "stockwise_dev_password"

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    GEMINI_API_KEY: str = ""
    FMP_API_KEY: str = ""

    class Config:
        env_file = _root_dir() / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
