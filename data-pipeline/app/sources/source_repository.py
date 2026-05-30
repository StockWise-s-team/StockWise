import logging
import time
from typing import List, Optional

import psycopg2
import psycopg2.extras

from app.config import settings
from app.sources.models import NewsSource

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 5 * 60  # 5 minutes


class SourceRepository:
    def __init__(self):
        self._cache: Optional[List[NewsSource]] = None
        self._cache_timestamp: float = 0.0

    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    def invalidate(self) -> None:
        self._cache = None
        self._cache_timestamp = 0.0
        logger.debug("[SourceRepository] Cache invalidated")

    def get_active_sources(self) -> List[NewsSource]:
        if self._is_cache_valid():
            logger.debug("[SourceRepository] Returning cached sources (%d)", len(self._cache))
            return self._cache

        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                cur.execute(
                    "SELECT id, name, base_url, crawler_type, is_active "
                    "FROM news_sources WHERE is_active = true"
                )
                rows = cur.fetchall()
                sources = [self._map_row(row) for row in rows]
                self._cache = sources
                self._cache_timestamp = time.monotonic()
                logger.info("[SourceRepository] Fetched %d active sources from DB", len(sources))
                return sources
            finally:
                cur.close()
                conn.close()
        except Exception as exc:
            logger.error("[SourceRepository] DB error fetching sources: %s", exc)
            if self._cache is not None:
                logger.warning("[SourceRepository] Returning stale cache due to DB error")
                return self._cache
            return []

    def _is_cache_valid(self) -> bool:
        if self._cache is None:
            return False
        elapsed = time.monotonic() - self._cache_timestamp
        return elapsed < _CACHE_TTL_SECONDS

    @staticmethod
    def _map_row(row: dict) -> NewsSource:
        return NewsSource(
            id=row["id"],
            name=row["name"],
            base_url=row["base_url"],
            crawler_type=row["crawler_type"],
            is_active=row["is_active"],
        )
