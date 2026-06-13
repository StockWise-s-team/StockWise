import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


def _root_dir() -> Path:
    # Path to the root CNPM/StockWise directory (where .env is located)
    return Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Database Configuration (supports DB_* and POSTGRES_* names)
    DB_HOST: str = "localhost"
    DB_PORT: int = 15432
    DB_NAME: str = "stockwise"
    DB_USERNAME: str = "stockwise"
    DB_PASSWORD: str = "stockwise_dev_password"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 15432
    POSTGRES_DB: str = "stockwise"
    POSTGRES_USER: str = "stockwise"
    POSTGRES_PASSWORD: str = "stockwise_dev_password"

    @property
    def DATABASE_URL(self) -> str:
        # Use whichever environment variables are populated, preferring DB_*
        host = os.getenv("DB_HOST", self.POSTGRES_HOST)
        port = os.getenv("DB_PORT", str(self.POSTGRES_PORT))
        db = os.getenv("DB_NAME", self.POSTGRES_DB)
        user = os.getenv("DB_USERNAME", self.POSTGRES_USER)
        pw = os.getenv("DB_PASSWORD", self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{db}"

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # RabbitMQ Configuration
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    # AI API Keys & Configuration
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GROQ_API_KEY: str = ""
    AI_ROUTING_PRIMARY_MODEL: str = "gpt-4o-mini"
    AI_ROUTING_FALLBACK_MODEL: str = "gemini-3.5-flash"
    AI_SAFETY_PRIMARY_MODEL: str = "gpt-4o-mini"
    AI_SAFETY_FALLBACK_MODEL: str = "gemini-3.5-flash"
    AI_ANALYST_PRIMARY_MODEL: str = "gpt-4o"
    AI_ANALYST_FALLBACK_MODEL: str = "gemini-3.5-flash"

    # Qdrant Vector DB (supports APP_* prefixes to avoid conflict)
    APP_QDRANT_HOST: str = "localhost"
    APP_QDRANT_PORT: int = 16333
    QDRANT_COLLECTION: str = "news_chunks"
    EMBEDDING_DIMENSION: int = 384

    @property
    def QDRANT_HOST(self) -> str:
        return self.APP_QDRANT_HOST

    @property
    def QDRANT_PORT(self) -> int:
        return self.APP_QDRANT_PORT

    # Service Integration URLs
    DATA_PIPELINE_URL: str = "http://localhost:8001"
    MARKET_SERVICE_URL: str = "http://localhost:8082"
    PORTFOLIO_SERVICE_URL: str = "http://localhost:8083"

    # AI & RAG Orchestration Config
    AI_RAG_MODE: str = "sql"  # options: 'sql' | 'hybrid' | 'disabled'
    AI_MAX_NEWS_RESULTS: int = 5
    AI_MAX_HISTORY_MESSAGES: int = 10
    AI_STALE_AFTER_DAYS: int = 3
    AI_DATA_MODE: str = "live"  # 'demo' | 'live'
    AI_MARKET_PROVIDER: str = "database"  # 'database' | 'http'
    AI_PORTFOLIO_PROVIDER: str = "database"  # 'database' | 'http'
    LLM_REQUEST_TIMEOUT_SECONDS: float = 30.0

    # Rate Limiting & Safety
    AI_RATE_LIMIT_PER_MINUTE: int = 60
    AI_REDIS_RATE_LIMIT_ENABLED: bool = False
    AI_RABBITMQ_ENABLED: bool = False

    # Authentication & Security
    AI_AUTH_MODE: str = "development"
    JWT_SECRET: str = "your-256-bit-secret-change-in-production"
    AI_TRUST_GATEWAY_HEADERS: bool = False
    JWT_ALGORITHM: str = "HS256"
    AI_JWT_USER_ID_CLAIM: str = "sub"
    AI_JWT_ROLE_CLAIM: str = "role"
    AI_DEMO_USER_ID: str = "00000000-0000-0000-0000-000000000001"

    class Config:
        env_file = _root_dir() / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
