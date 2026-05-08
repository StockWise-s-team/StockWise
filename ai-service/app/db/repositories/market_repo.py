from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class MarketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ohlcv(self, symbol: str, limit: int = 30) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT symbol, trade_date, open, high, low, close, volume
                FROM stock_prices
                WHERE symbol = :symbol
                ORDER BY trade_date DESC
                LIMIT :limit
                """
            ),
            {"symbol": symbol.upper(), "limit": limit},
        )
        return [dict(row._mapping) for row in result]

    async def get_latest_price(self, symbol: str) -> dict[str, Any] | None:
        result = await self.session.execute(
            text(
                """
                SELECT symbol, trade_date, open, high, low, close, volume
                FROM stock_prices
                WHERE symbol = :symbol
                ORDER BY trade_date DESC
                LIMIT 1
                """
            ),
            {"symbol": symbol.upper()},
        )
        row = result.first()
        return dict(row._mapping) if row else None

    async def get_financial_ratios(self, symbol: str) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT symbol, period, pe_ratio, pb_ratio, eps, roe, roa
                FROM financial_ratios
                WHERE symbol = :symbol
                ORDER BY period DESC NULLS LAST
                """
            ),
            {"symbol": symbol.upper()},
        )
        return [dict(row._mapping) for row in result]
