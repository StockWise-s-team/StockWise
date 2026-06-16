"""
stream_d / fetcher.py
=====================
Fetch intraday OHLCV bars cho ngay hien tai qua vnstock.Quote.history().

Moi symbol -> goi q.history(start=today, end=today, interval="5m", length=50).
Tra ve danh sach OHLCV dicts.

Nguon: vnstock Quote.history() (kbs source)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

BATCH_SIZE = 20          # symbols per concurrent call
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 15
INTERVAL = "5m"
LENGTH = 50              # max ~72 bars/ngay voi 5m


class IntradayFetcher:
    """Batch-fetch intraday bars qua vnstock Quote.history()."""

    @property
    def source_name(self) -> str:
        return "vnstock_quote_history"

    async def fetch(self, symbols: list[str]) -> list[dict[str, Any]]:
        """Fetch intraday bars cho tat ca symbols, tra ve list records."""
        results: list[dict[str, Any]] = []

        batches = [
            symbols[i: i + BATCH_SIZE]
            for i in range(0, len(symbols), BATCH_SIZE)
        ]

        for batch in batches:
            batch_results = await self._fetch_batch(batch)
            results.extend(batch_results)

        return results

    async def _fetch_batch(self, symbols: list[str]) -> list[dict[str, Any]]:
        """Goi song song cho cac symbols trong 1 batch."""
        tasks = [self._fetch_one_with_retry(sym) for sym in symbols]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _fetch_one_with_retry(self, symbol: str) -> dict[str, Any]:
        """Fetch mot symbol, retry neu that bai."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                df = await asyncio.to_thread(self._call_history, symbol)
                records = self._df_to_records(df, symbol)
                return {
                    "symbol": symbol,
                    "records": records,
                }
            except Exception as e:
                logger.warning(
                    "[IntradayFetcher] %s attempt %d/%d failed: %s: %s",
                    symbol, attempt, MAX_RETRIES, type(e).__name__, e,
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
                else:
                    return {
                        "symbol": symbol,
                        "error": f"{type(e).__name__}: {e}",
                    }
        return {"symbol": symbol, "error": "Unexpected error"}

    @staticmethod
    def _call_history(symbol: str) -> pd.DataFrame:
        import vnstock

        vnstock.config.API_KEY = settings.VNSTOCK_API_KEY or ""
        today = datetime.now().strftime("%Y-%m-%d")
        q = vnstock.Quote(source="kbs", symbol=symbol)
        return q.history(
            start=today,
            end=today,
            interval=INTERVAL,
            length=LENGTH,
        )

    @staticmethod
    def _df_to_records(df: pd.DataFrame, symbol: str) -> list[dict[str, Any]]:
        """Chuan hoa DataFrame thanh list OHLCV dicts, gia nhan 1000."""
        if df is None or df.empty:
            return []

        now_iso = datetime.now(timezone.utc).isoformat()
        records: list[dict[str, Any]] = []

        for _, row in df.iterrows():
            raw_close = _float(row.get("close"))
            if raw_close is None:
                continue

            records.append({
                "symbol": symbol,
                "time": str(row.get("time", "")),
                "interval": INTERVAL,
                "open":   _round1000(_float(row.get("open"))) if _float(row.get("open")) is not None else None,
                "high":   _round1000(_float(row.get("high"))) if _float(row.get("high")) is not None else None,
                "low":    _round1000(_float(row.get("low")))  if _float(row.get("low"))  is not None else None,
                "close":  _round1000(raw_close),
                "volume": int(row.get("volume", 0) or 0),
                "timestamp": now_iso,
            })

        return records


def _float(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _round1000(v: float | None) -> float | None:
    if v is None:
        return None
    return round(v * 1000, 1)
