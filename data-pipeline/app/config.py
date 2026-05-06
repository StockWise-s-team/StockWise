from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "stockwise"
    POSTGRES_USER: str = "stockwise"
    POSTGRES_PASSWORD: str = "stockwise_dev_password"

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"

    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    GEMINI_API_KEY: str = ""

    CK_API_BASE_URL: str = ""
    CK_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
