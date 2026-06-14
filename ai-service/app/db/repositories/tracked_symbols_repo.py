from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TrackedSymbolsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tracked_symbols(self, user_id: str) -> dict[str, Any]:
        system_result = await self.session.execute(
            text("SELECT symbol FROM tracked_symbols ORDER BY symbol")
        )
        system_symbols = [str(row.symbol) for row in system_result]

        user_symbols: list[str] = []
        if user_id:
            user_result = await self.session.execute(
                text(
                    """
                    SELECT symbol
                    FROM user_tracked_symbols
                    WHERE user_id = CAST(:user_id AS uuid)
                    ORDER BY symbol
                    """
                ),
                {"user_id": user_id},
            )
            user_symbols = [str(row.symbol) for row in user_result]

        active_symbols = user_symbols or system_symbols
        return {
            "user_id": user_id,
            "tracked_symbols": active_symbols,
            "user_tracked_symbols": user_symbols,
            "system_tracked_symbols": system_symbols,
            "selection_scope": "user" if user_symbols else "system",
        }
