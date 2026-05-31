import logging
import time
from typing import List, Optional

import psycopg2
import psycopg2.extras

from app.config import settings
from app.sources.models import NewsSource

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 5 * 60  # 5 minutes

_cache: Optional[List[NewsSource]] = None
_cache_timestamp: float = 0.0


class SourceRepository:
    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    def invalidate(self) -> None:
        global _cache, _cache_timestamp
        _cache = None
        _cache_timestamp = 0.0
        logger.debug("[SourceRepository] Cache invalidated")

    def get_active_sources(self) -> List[NewsSource]:
        global _cache, _cache_timestamp
        if self._is_cache_valid():
            logger.debug("[SourceRepository] Returning cached sources (%d)", len(_cache))
            return _cache

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
                _cache = sources
                _cache_timestamp = time.monotonic()
                logger.info("[SourceRepository] Fetched %d active sources from DB", len(sources))
                return sources
            finally:
                cur.close()
                conn.close()
        except Exception as exc:
            logger.error("[SourceRepository] DB error fetching sources: %s", exc)
            if _cache is not None:
                logger.warning("[SourceRepository] Returning stale cache due to DB error")
                return _cache
            return []

    def _is_cache_valid(self) -> bool:
        global _cache, _cache_timestamp
        if _cache is None:
            return False
        elapsed = time.monotonic() - _cache_timestamp
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
