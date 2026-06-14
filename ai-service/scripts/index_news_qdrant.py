import asyncio
import sys
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.db.database import AsyncSessionLocal
from app.services.news_retriever import hashed_embedding


async def load_articles() -> list[dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(
                """
                SELECT id, title, content, url, symbols, published_at, crawled_at
                FROM news_articles
                ORDER BY COALESCE(published_at, crawled_at) DESC
                """
            )
        )
        return [dict(row._mapping) for row in result]


async def index_news() -> None:
    articles = await load_articles()
    base_url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.put(
            f"{base_url}/collections/{settings.QDRANT_COLLECTION}",
            json={"vectors": {"size": settings.EMBEDDING_DIMENSION, "distance": "Cosine"}},
        )
        if response.status_code not in {200, 409}:
            response.raise_for_status()
        points = [
            {
                "id": str(article["id"]),
                "vector": hashed_embedding(f"{article['title']} {article.get('content') or ''}", settings.EMBEDDING_DIMENSION),
                "payload": {
                    **article,
                    "id": str(article["id"]),
                    "published_at": article["published_at"].isoformat() if article.get("published_at") else None,
                    "crawled_at": article["crawled_at"].isoformat() if article.get("crawled_at") else None,
                },
            }
            for article in articles
        ]
        if points:
            (await client.put(f"{base_url}/collections/{settings.QDRANT_COLLECTION}/points", json={"points": points})).raise_for_status()
    print(f"Indexed {len(articles)} news articles into {settings.QDRANT_COLLECTION}.")


if __name__ == "__main__":
    asyncio.run(index_news())
