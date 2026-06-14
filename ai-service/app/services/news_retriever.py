import logging
import math
import re
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Protocol

import httpx

from app.config import settings
from app.db.repositories.content_repo import ContentRepository

logger = logging.getLogger(__name__)


class NewsRetriever(Protocol):
    async def search(self, symbol: str, limit: int) -> list[dict[str, Any]]:
        ...


class SQLNewsRetriever:
    def __init__(self, repository: ContentRepository):
        self.repository = repository

    async def search(self, symbol: str, limit: int) -> list[dict[str, Any]]:
        return await self.repository.get_recent_articles(symbol, limit=limit)


class HybridNewsRetriever:
    """Prefer an optional semantic retriever and preserve SQL as an explicit fallback."""

    def __init__(self, semantic: NewsRetriever, sql_fallback: NewsRetriever):
        self.semantic = semantic
        self.sql_fallback = sql_fallback

    async def search(self, symbol: str, limit: int) -> list[dict[str, Any]]:
        try:
            articles = await self.semantic.search(symbol, limit)
            if articles:
                return articles
        except Exception as exc:
            logger.warning("Semantic news retrieval failed, using SQL fallback: %s", exc)
        return await self.sql_fallback.search(symbol, limit)


class QdrantNewsRetriever:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client = client
        self.base_url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}"

    async def search(self, symbol: str, limit: int) -> list[dict[str, Any]]:
        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
        payload = {
            "vector": hashed_embedding(symbol, settings.EMBEDDING_DIMENSION),
            "limit": max(1, min(limit, 20)),
            "with_payload": True,
            "filter": {
                "must": [
                    {"key": "symbols", "match": {"any": [symbol.upper()]}},
                    {"key": "published_at", "range": {"gte": since.isoformat()}},
                ]
            },
        }
        response = await self._post(f"/collections/{settings.QDRANT_COLLECTION}/points/search", payload)
        return [item["payload"] for item in response.get("result", []) if item.get("payload")]

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.client:
            response = await self.client.post(f"{self.base_url}{path}", json=payload)
        else:
            async with httpx.AsyncClient(timeout=3) as client:
                response = await client.post(f"{self.base_url}{path}", json=payload)
        response.raise_for_status()
        return response.json()


class DisabledNewsRetriever:
    async def search(self, symbol: str, limit: int) -> list[dict[str, Any]]:
        return []


def hashed_embedding(text: str, dimension: int) -> list[float]:
    """Build deterministic local vectors so optional indexing needs no paid API."""
    vector = [0.0] * dimension
    for token in re.findall(r"\w+", text.lower()):
        digest = sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:4], "big") % dimension] += 1.0
    norm = math.sqrt(sum(item * item for item in vector)) or 1.0
    return [item / norm for item in vector]


def create_news_retriever(repository: ContentRepository) -> NewsRetriever:
    sql = SQLNewsRetriever(repository)
    if settings.AI_RAG_MODE == "sql":
        return sql
    if settings.AI_RAG_MODE == "hybrid":
        return HybridNewsRetriever(QdrantNewsRetriever(), sql)
    if settings.AI_RAG_MODE == "disabled":
        return DisabledNewsRetriever()
    raise ValueError("Unsupported AI_RAG_MODE")
