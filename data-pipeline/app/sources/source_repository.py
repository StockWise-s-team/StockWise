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
    _cache: Optional[List[NewsSource]] = None
    _cache_timestamp: float = 0.0

    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    def invalidate(self) -> None:
        import json
        _log_path = "d:/StockWise/debug-07e1c9.log"
        _log_id = f"log_{int(time.monotonic()*1000000)}"
        try:
            with open(_log_path, "a") as _f:
                _f.write(json.dumps({
                    "id": f"{_log_id}_invalidate",
                    "timestamp": int(time.time()*1000),
                    "location": "source_repository.py:invalidate",
                    "message": "Cache invalidated",
                    "runId": "hypothesis-test",
                    "hypothesisId": "H2+H3",
                    "data": {"cache_was_count": len(self._cache) if self._cache is not None else 0}
                }) + "\n")
        except: pass
        SourceRepository._cache = None
        SourceRepository._cache_timestamp = 0.0
        self._cache = None
        self._cache_timestamp = 0.0
        logger.debug("[SourceRepository] Cache invalidated")

    def get_active_sources(self) -> List[NewsSource]:
        import json
        _log_path = "d:/StockWise/debug-07e1c9.log"
        _log_id = f"log_{int(time.monotonic()*1000000)}"
        def _w(loc, msg, hid, extra=None):
            try:
                d = {"id": f"{_log_id}_{loc}", "timestamp": int(time.time()*1000),
                     "location": f"source_repository.py:get_active_sources:{loc}",
                     "message": msg, "runId": "hypothesis-test", "hypothesisId": hid}
                if extra: d["data"] = extra
                with open(_log_path, "a") as _f: _f.write(json.dumps(d) + "\n")
            except: pass
        _w("entry", "get_active_sources entry", "H1+H2+H3",
           {"cache_valid": self._is_cache_valid(), "cache_len": len(self._cache) if self._cache is not None else None})

        if self._is_cache_valid():
            logger.debug("[SourceRepository] Returning cached sources (%d)", len(self._cache))
            _w("cache_hit", f"Returning cached sources ({len(self._cache)})", "H2",
               {"cached_source_ids": [str(s.id) for s in self._cache], "cache_count": len(self._cache)})
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
                SourceRepository._cache = sources
                SourceRepository._cache_timestamp = time.monotonic()
                self._cache = sources
                self._cache_timestamp = SourceRepository._cache_timestamp
                logger.info("[SourceRepository] Fetched %d active sources from DB", len(sources))
                _w("db_fetch", f"Fetched {len(sources)} sources from DB", "H1+H2+H3",
                   {"source_count": len(sources), "source_ids": [str(s.id) for s in sources]})
                return sources
            finally:
                cur.close()
                conn.close()
        except Exception as exc:
            logger.error("[SourceRepository] DB error fetching sources: %s", exc)
            _w("db_error", f"DB error: {exc}", "H1+H3",
               {"error": str(exc), "cache_available": self._cache is not None, "cache_len": len(self._cache) if self._cache is not None else None})
            if self._cache is not None:
                logger.warning("[SourceRepository] Returning stale cache due to DB error")
                _w("stale_cache", f"Returning stale cache ({len(self._cache)} sources)", "H3",
                   {"stale_source_ids": [str(s.id) for s in self._cache]})
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

