import logging
from typing import Any

import yfinance as yf

from app.stream_a.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class YahooFinanceFetcher(BaseFetcher):
    @property
    def source_name(self) -> str:
        return "yahoo_finance"

    async def fetch(self, symbols: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for symbol in symbols:
            try:
                ratios = self._fetch_ratios(symbol)
                results.append({"symbol": symbol, "ratios": ratios})
                logger.info("[YahooFinanceFetcher] Fetched ratios for %s", symbol)
            except Exception as e:
                logger.warning(
                    "[YahooFinanceFetcher] Failed to fetch ratios for %s: %s",
                    symbol,
                    e,
                )
                results.append({"symbol": symbol, "ratios": {}})
        return results

    def _fetch_ratios(self, symbol: str) -> dict[str, Any]:
        ticker = yf.Ticker(f"{symbol}.VN")
        info = ticker.info or {}

        def safe_float(value: Any) -> float | None:
            if value is None or value == "N/A" or value == "":
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        ratios: dict[str, Any] = {}

        ratios["pe_ratio"] = safe_float(info.get("trailingPE"))
        ratios["pb_ratio"] = safe_float(info.get("priceToBook"))
        ratios["eps"] = safe_float(info.get("trailingEps"))
        ratios["roe"] = safe_float(info.get("returnOnEquity"))
        ratios["roa"] = safe_float(info.get("returnOnAssets"))
        ratios["period"] = "ttm"

        return {k: v for k, v in ratios.items() if v is not None}
