from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class PortfolioRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_portfolio(self, user_id: str) -> dict[str, Any] | None:
        portfolio_result = await self.session.execute(
            text(
                """
                SELECT id, user_id, virtual_cash
                FROM portfolios
                WHERE user_id = CAST(:user_id AS uuid)
                LIMIT 1
                """
            ),
            {"user_id": user_id},
        )
        portfolio = portfolio_result.first()
        if not portfolio:
            return None

        holdings_result = await self.session.execute(
            text(
                """
                SELECT h.symbol, h.quantity, h.avg_price, latest.close AS latest_close,
                       (h.quantity * COALESCE(latest.close, 0)) AS market_value,
                       (h.quantity * (COALESCE(latest.close, h.avg_price) - h.avg_price)) AS unrealized_pnl,
                       latest.trade_date AS market_updated_at
                FROM holdings h
                LEFT JOIN LATERAL (
                    SELECT close, trade_date
                    FROM stock_prices
                    WHERE symbol = h.symbol
                    ORDER BY trade_date DESC
                    LIMIT 1
                ) latest ON true
                WHERE h.portfolio_id = :portfolio_id
                ORDER BY h.symbol
                """
            ),
            {"portfolio_id": portfolio.id},
        )
        holdings = [dict(row._mapping) for row in holdings_result]
        total_value = sum(float(item["market_value"] or 0) for item in holdings)
        total_pnl = sum(float(item["unrealized_pnl"] or 0) for item in holdings)
        return {
            "user_id": str(portfolio.user_id),
            "virtual_cash": float(portfolio.virtual_cash or 0),
            "holdings": holdings,
            "total_value": total_value,
            "unrealized_pnl": total_pnl,
        }
