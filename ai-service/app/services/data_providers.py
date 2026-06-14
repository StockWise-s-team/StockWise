from datetime import date, timedelta
from typing import Any, Protocol

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.repositories.market_repo import MarketRepository
from app.db.repositories.portfolio_repo import PortfolioRepository


class MarketDataProvider(Protocol):
    async def get_latest_price(self, symbol: str) -> dict[str, Any] | None:
        ...

    async def get_financial_ratios(self, symbol: str, limit: int = 8) -> list[dict[str, Any]]:
        ...

    async def get_ohlcv(self, symbol: str, limit: int = 30) -> list[dict[str, Any]]:
        ...


class PortfolioProvider(Protocol):
    async def get_portfolio(self, user_id: str) -> dict[str, Any] | None:
        ...


class HTTPMarketDataProvider:
    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.client = client

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if self.client:
            response = await self.client.get(f"{self.base_url}{path}", params=params)
        else:
            async with httpx.AsyncClient(timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.get(f"{self.base_url}{path}", params=params)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def get_latest_price(self, symbol: str) -> dict[str, Any] | None:
        payload = await self._get(f"/market/price/{symbol.upper()}")
        return self._normalize_price(payload) if payload else None

    async def get_financial_ratios(self, symbol: str, limit: int = 8) -> list[dict[str, Any]]:
        payload = await self._get(f"/market/ratio/{symbol.upper()}") or []
        return [
            {
                "symbol": item["symbol"],
                "period": item.get("period"),
                "pe_ratio": item.get("peRatio"),
                "pb_ratio": item.get("pbRatio"),
                "eps": item.get("eps"),
                "roe": item.get("roe"),
                "roa": item.get("roa"),
            }
            for item in payload[: max(1, min(limit, 20))]
        ]

    async def get_ohlcv(self, symbol: str, limit: int = 30) -> list[dict[str, Any]]:
        bounded_limit = max(1, min(limit, 365))
        end_date = date.today()
        payload = await self._get(
            f"/market/ohlc/{symbol.upper()}",
            {"startDate": (end_date - timedelta(days=bounded_limit * 2)).isoformat(), "endDate": end_date.isoformat()},
        ) or []
        return [self._normalize_price(item) for item in payload[-bounded_limit:]]

    def _normalize_price(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "symbol": item["symbol"],
            "trade_date": item["tradeDate"],
            "open": item.get("open"),
            "high": item.get("high"),
            "low": item.get("low"),
            "close": item.get("close"),
            "volume": item.get("volume"),
        }


class HTTPPortfolioProvider:
    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.client = client

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        if self.client:
            response = await self.client.get(f"{self.base_url}{path}", params=params)
        else:
            async with httpx.AsyncClient(timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.get(f"{self.base_url}{path}", params=params)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def get_portfolio(self, user_id: str) -> dict[str, Any] | None:
        payload = await self._get("/portfolio", {"userId": user_id})
        if not payload:
            return None
        pnl = await self._get("/portfolio/pnl", {"userId": user_id}) or {}
        portfolio = payload.get("portfolio", {})
        return {
            "user_id": user_id,
            "virtual_cash": portfolio.get("virtualCash", 0),
            "holdings": payload.get("holdings", []),
            "total_value": None,
            "unrealized_pnl": pnl.get("totalPnl"),
            "data_limitations": ["portfolio-service does not expose current total market value"],
        }


def create_market_provider(db: AsyncSession) -> MarketDataProvider:
    if settings.AI_MARKET_PROVIDER == "database":
        return MarketRepository(db)
    if settings.AI_MARKET_PROVIDER == "http":
        return HTTPMarketDataProvider(settings.MARKET_SERVICE_URL)
    raise ValueError("Unsupported AI_MARKET_PROVIDER")


def create_portfolio_provider(db: AsyncSession) -> PortfolioProvider:
    if settings.AI_PORTFOLIO_PROVIDER == "database":
        return PortfolioRepository(db)
    if settings.AI_PORTFOLIO_PROVIDER == "http":
        return HTTPPortfolioProvider(settings.PORTFOLIO_SERVICE_URL)
    raise ValueError("Unsupported AI_PORTFOLIO_PROVIDER")
