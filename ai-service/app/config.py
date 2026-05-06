from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "stockwise"
    DB_USERNAME: str = "stockwise"
    DB_PASSWORD: str = "stockwise_dev_password"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

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
