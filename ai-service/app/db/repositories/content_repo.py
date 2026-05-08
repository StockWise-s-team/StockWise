from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ContentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_sources(self) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT id, name, base_url, crawler_type, is_active, created_at
                FROM news_sources
                ORDER BY created_at DESC
                """
            )
        )
        return [dict(row._mapping) for row in result]

    async def add_source(self, name: str, base_url: str, crawler_type: str) -> dict[str, Any]:
        result = await self.session.execute(
            text(
                """
                INSERT INTO news_sources (name, base_url, crawler_type, is_active)
                VALUES (:name, :base_url, :crawler_type, true)
                RETURNING id, name, base_url, crawler_type, is_active, created_at
                """
            ),
            {"name": name, "base_url": str(base_url), "crawler_type": crawler_type},
        )
        await self.session.commit()
        return dict(result.one()._mapping)

    async def toggle_source(self, source_id: str) -> dict[str, Any] | None:
        result = await self.session.execute(
            text(
                """
                UPDATE news_sources
                SET is_active = NOT is_active
                WHERE id = CAST(:source_id AS uuid)
                RETURNING id, name, base_url, crawler_type, is_active, created_at
                """
            ),
            {"source_id": source_id},
        )
        row = result.first()
        await self.session.commit()
        return dict(row._mapping) if row else None

    async def deactivate_source(self, source_id: str) -> dict[str, Any] | None:
        result = await self.session.execute(
            text(
                """
                UPDATE news_sources
                SET is_active = false
                WHERE id = CAST(:source_id AS uuid)
                RETURNING id, name, base_url, crawler_type, is_active, created_at
                """
            ),
            {"source_id": source_id},
        )
        row = result.first()
        await self.session.commit()
        return dict(row._mapping) if row else None

    async def get_wiki(self, symbol: str) -> dict[str, Any] | None:
        result = await self.session.execute(
            text(
                """
                SELECT symbol, wiki_data, version, updated_at
                FROM company_wiki
                WHERE symbol = :symbol
                """
            ),
            {"symbol": symbol.upper()},
        )
        row = result.first()
        return dict(row._mapping) if row else None

    async def get_wiki_history(self, symbol: str) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT symbol, wiki_data, version, created_at
                FROM company_wiki_history
                WHERE symbol = :symbol
                ORDER BY version DESC, created_at DESC
                """
            ),
            {"symbol": symbol.upper()},
        )
        return [dict(row._mapping) for row in result]
