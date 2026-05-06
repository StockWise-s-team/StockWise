import psycopg2
from typing import List
from app.config import settings
from app.sources.models import NewsSource

class SourceRepository:
    def get_active_sources(self) -> List[NewsSource]:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST, dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD
        )
        return []
