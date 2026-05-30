import asyncio
import logging
from typing import Any, Dict, List

import httpx

from app.config import settings
from app.stream_a.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT_SECONDS = 15
FMP_BASE_URL = "https://financialmodelingprep.com/stable"


class CkApiFetcher(BaseFetcher):
    @property
    def source_name(self) -> str:
        return "ck_api"

    async def fetch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        if not settings.FMP_API_KEY:
            logger.warning(
                "[CkApiFetcher] FMP_API_KEY not configured — "
                "returning empty results"
            )
            return [{"symbol": s, "ratios": {}} for s in symbols]

        results: List[Dict[str, Any]] = []

        for symbol in symbols:
            try:
                ratios = await self._fetch_symbol(symbol)
                results.append({"symbol": symbol, "ratios": ratios})
                logger.info(
                    f"[CkApiFetcher] Fetched ratios for {symbol}"
                )
            except Exception as e:
                logger.warning(
                    f"[CkApiFetcher] Failed to fetch ratios for {symbol}: "
                    f"{type(e).__name__}: {e}"
                )
                results.append({"symbol": symbol, "ratios": {}})

        return results

    async def _fetch_symbol(self, symbol: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{FMP_BASE_URL}/ratios-ttm",
                params={
                    "symbol": symbol,
                    "apikey": settings.FMP_API_KEY,
                },
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                return self._parse_response(data[0], symbol)
            elif isinstance(data, dict) and data.get("Error Message"):
                raise ValueError(data["Error Message"])
            else:
                raise ValueError(f"Unexpected FMP response format: {data}")

    @staticmethod
    def _parse_response(raw: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        def safe_float(value: Any) -> float | None:
            if value is None or value == "None" or value == "":
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        ratios: Dict[str, Any] = {}

        ratios["pe_ratio"]  = safe_float(raw.get("priceToEarningsRatioTTM"))
        ratios["pb_ratio"]  = safe_float(raw.get("priceToBookRatioTTM"))
        ratios["eps"]       = safe_float(raw.get("epsTTM"))
        ratios["roe"]       = safe_float(raw.get("returnOnEquityTTM"))
        ratios["roa"]       = safe_float(raw.get("returnOnAssetsTTM"))
        ratios["period"]    = "ttm"

        return {k: v for k, v in ratios.items() if v is not None}
