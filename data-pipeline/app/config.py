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

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    APP_QDRANT_HOST: str = "qdrant"
    APP_QDRANT_PORT: int = 16333

    GEMINI_API_KEY: str = ""
    FMP_API_KEY: str = ""
    VNSTOCK_API_KEY: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_LLM_MODEL: str = "gpt-5.4-mini"
    OPENAI_LLM_REASONING_EFFORT: str = "xhigh"
    EMBEDDING_MODEL: str = "openai"
    EMBEDDING_DIM: int = 1536

    class Config:
        env_file = _root_dir() / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
