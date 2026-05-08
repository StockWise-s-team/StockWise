from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "stockwise"
    POSTGRES_USER: str = "stockwise"
    POSTGRES_PASSWORD: str = "stockwise_dev_password"
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DATA_PIPELINE_URL: str = "http://data-pipeline:8001"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
