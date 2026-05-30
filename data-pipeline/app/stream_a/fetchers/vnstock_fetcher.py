import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import vnstock

from app.config import settings
from app.stream_a.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL = "1D"
DEFAULT_DAYS_BACK = 30
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


class VnStockFetcher(BaseFetcher):
    def __init__(
        self,
        interval: str = DEFAULT_INTERVAL,
        days_back: int = DEFAULT_DAYS_BACK,
    ):
        self.interval = interval
        self.days_back = days_back

    @property
    def source_name(self) -> str:
        return "vnstock"

    async def fetch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days_back)

        results: List[Dict[str, Any]] = []

        for symbol in symbols:
            try:
                data = await self._fetch_symbol(symbol, start_date, end_date)
                results.append({"symbol": symbol, "prices": data})
                logger.info(
                    f"[VnStockFetcher] Fetched {len(data)} bars for {symbol}"
                )
            except Exception as e:
                logger.warning(
                    f"[VnStockFetcher] Failed to fetch {symbol}: {type(e).__name__}: {e}"
                )
                results.append({"symbol": symbol, "prices": [], "error": str(e)})

        return results

    async def _fetch_symbol(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        norm_symbol = self._normalize_symbol(symbol)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                df = await asyncio.to_thread(
                    self._call_history,
                    norm_symbol,
                    start_date,
                    end_date,
                )
                if df is not None and not df.empty:
                    return self._df_to_price_list(df, norm_symbol)
            except Exception as e:
                logger.warning(
                    f"[VnStockFetcher] attempt {attempt}/{MAX_RETRIES} failed for "
                    f"{symbol}: {type(e).__name__}: {e}"
                )
                if attempt == MAX_RETRIES:
                    raise
                await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)

        raise ValueError(f"All sources failed for {symbol}")

    @staticmethod
    def _call_history(
        symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        q = vnstock.Quote(symbol=symbol)
        return q.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval="1D",
        )

    @staticmethod
    def _normalize_symbol(raw: str) -> str:
        return raw.strip().upper()

    @staticmethod
    def _df_to_price_list(df: pd.DataFrame, symbol: str) -> List[Dict[str, Any]]:
        rename_map = {
            "time": "date",
            "Time": "date",
            "datetime": "date",
            "Date": "date",
            "open": "open",
            "Open": "open",
            "high": "high",
            "High": "high",
            "low": "low",
            "Low": "low",
            "close": "close",
            "Close": "close",
            "volume": "volume",
            "Volume": "volume",
        }

        df = df.rename(columns=rename_map)

        required = {"date", "open", "high", "low", "close", "volume"}
        if not required.issubset(df.columns):
            missing = required - set(df.columns)
            raise ValueError(f"Missing columns after rename: {missing}")

        df["date"] = df["date"].astype(str)

        return df[["date", "open", "high", "low", "close", "volume"]].to_dict(
            orient="records"
        )
