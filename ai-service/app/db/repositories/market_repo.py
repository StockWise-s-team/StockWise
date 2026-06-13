from datetime import date, datetime
from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class MarketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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
        if not row:
            return None
        data = dict(row._mapping)
        if isinstance(data.get("trade_date"), (date, datetime)):
            data["trade_date"] = data["trade_date"].isoformat()
        for key in ["open", "high", "low", "close"]:
            if data.get(key) is not None:
                data[key] = float(data[key])
        return data

    async def get_financial_ratios(self, symbol: str, limit: int = 8) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT symbol, period, pe_ratio, pb_ratio, eps, roe, roa
                FROM financial_ratios
                WHERE symbol = :symbol
                ORDER BY period DESC
                LIMIT :limit
                """
            ),
            {"symbol": symbol.upper(), "limit": limit},
        )
        rows = result.all()
        ratios = []
        for row in rows:
            data = dict(row._mapping)
            for key in ["pe_ratio", "pb_ratio", "eps", "roe", "roa"]:
                if data.get(key) is not None:
                    data[key] = float(data[key])
            ratios.append(data)
        return ratios

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
        rows = result.all()
        ohlcv = []
        for row in reversed(rows):
            data = dict(row._mapping)
            if isinstance(data.get("trade_date"), (date, datetime)):
                data["trade_date"] = data["trade_date"].isoformat()
            for key in ["open", "high", "low", "close"]:
                if data.get(key) is not None:
                    data[key] = float(data[key])
            ohlcv.append(data)
        return ohlcv
