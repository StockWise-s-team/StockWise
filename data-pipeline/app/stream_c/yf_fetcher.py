"""
stream_c / yf_fetcher.py
=========================
Fallback fetcher dùng yfinance khi vnstock bị rate limit.

Dùng yfinance.download() — 1 HTTP request cho toàn bộ batch symbols.
Trả về OHLCV của ngày giao dịch gần nhất + tính percent_change từ previous_close.

Lưu ý về độ trễ:
  - interval="1d": chỉ cập nhật dữ liệu cuối ngày (không real-time intraday)
  - interval="1m": gần real-time hơn nhưng Yahoo VN có lag ~10-15 phút
  → Đây là fallback khi vnstock rate limit, không phải nguồn primary.

Fields trả về (tương thích với PriceBoardFetcher):
    symbol, close, open, high, low, volume,
    reference_price (= previous_close), percent_change, timestamp
    [THIẾU so với vnstock: ceiling_price, floor_price, average_price, bid/ask]
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

# Kích thước batch gửi sang yfinance (hỗ trợ lớn, Yahoo API không limit như KBS)
BATCH_SIZE = 100
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


class YahooFinancePriceFetcher:
    """
    Fallback fetcher: lấy giá OHLCV cuối phiên gần nhất qua Yahoo Finance.
    Không bị rate limit như vnstock, nhưng có delay ~15 phút (hoặc cuối ngày).
    """

    @property
    def source_name(self) -> str:
        return "yahoo_finance_price"

    async def fetch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Fetch giá OHLCV cho list symbols. Trả về format tương thích với PriceBoardFetcher."""
        results: List[Dict[str, Any]] = []

        batches = [
            symbols[i : i + BATCH_SIZE]
            for i in range(0, len(symbols), BATCH_SIZE)
        ]

        for batch in batches:
            try:
                batch_data = await self._fetch_batch(batch)
                results.extend(batch_data)
            except Exception as e:
                logger.warning(
                    "[YFPriceFetcher] Batch failed for %s: %s: %s",
                    batch,
                    type(e).__name__,
                    e,
                )
                for sym in batch:
                    results.append({"symbol": sym, "error": str(e)})

        return results

    async def _fetch_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                df, prev_df = await asyncio.to_thread(self._call_download, symbols)
                return self._parse_results(symbols, df, prev_df)
            except Exception as e:
                logger.warning(
                    "[YFPriceFetcher] attempt %d/%d failed: %s",
                    attempt, MAX_RETRIES, e,
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
                else:
                    raise

        raise RuntimeError("Unreachable")

    @staticmethod
    def _call_download(symbols: List[str]):
        """
        Gọi yfinance.download — sync, chạy trong thread riêng.
        Tải 2 ngày để lấy được previous_close (dùng tính % thay đổi).
        """
        import yfinance as yf

        yf_syms = [f"{s}.VN" for s in symbols]
        tickers_str = " ".join(yf_syms)

        df = yf.download(
            tickers=tickers_str,
            period="2d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
        )
        return df, None  # prev_df không cần, lấy từ df.iloc[-2]

    def _parse_results(
        self,
        symbols: List[str],
        df: pd.DataFrame,
        _prev_df,
    ) -> List[Dict[str, Any]]:
        """Chuyển DataFrame multi-level columns thành list dict."""
        if df is None or df.empty:
            return [{"symbol": s, "error": "empty dataframe"} for s in symbols]

        now_iso = datetime.now(timezone.utc).isoformat()
        records: List[Dict[str, Any]] = []

        for sym in symbols:
            yf_sym = f"{sym}.VN"
            try:
                # Multi-ticker download → cột dạng (OHLCV, TICKER)
                if yf_sym in df.columns.get_level_values(1) if hasattr(df.columns, 'get_level_values') else []:
                    sub = df.xs(yf_sym, axis=1, level=1).dropna(how="all")
                elif yf_sym in df.columns.get_level_values(0) if hasattr(df.columns, 'get_level_values') else []:
                    sub = df[yf_sym].dropna(how="all")
                else:
                    # Trường hợp chỉ 1 symbol (không có multi-level)
                    sub = df.dropna(how="all")

                if sub is None or sub.empty:
                    records.append({"symbol": sym, "error": "no data for symbol"})
                    continue

                # Lấy hàng cuối (ngày giao dịch gần nhất)
                latest = sub.iloc[-1]
                prev_close = float(sub.iloc[-2]["Close"]) if len(sub) >= 2 else None

                close = self._safe_float(latest.get("Close"))
                if close is None:
                    records.append({"symbol": sym, "error": "no close price"})
                    continue

                pct = None
                if close and prev_close and prev_close > 0:
                    pct = round((close - prev_close) / prev_close * 100, 4)

                records.append({
                    "symbol":           sym,
                    "close":            close,
                    "open":             self._safe_float(latest.get("Open")),
                    "high":             self._safe_float(latest.get("High")),
                    "low":              self._safe_float(latest.get("Low")),
                    "volume":           self._safe_int(latest.get("Volume")),
                    "reference_price":  prev_close,   # giá TC = previous_close
                    "price_change":     round(close - prev_close, 2) if close and prev_close else None,
                    "percent_change":   pct,
                    # Các field vnstock có nhưng Yahoo không có:
                    "ceiling_price":    None,
                    "floor_price":      None,
                    "average_price":    None,
                    "timestamp":        now_iso,
                    "source":           "yahoo_finance",
                })

            except Exception as e:
                logger.warning("[YFPriceFetcher] Parse error for %s: %s", sym, e)
                records.append({"symbol": sym, "error": str(e)})

        return records

    @staticmethod
    def _safe_float(val: Any) -> float | None:
        if val is None:
            return None
        try:
            f = float(val)
            return None if pd.isna(f) else f
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_int(val: Any) -> int:
        if val is None:
            return 0
        try:
            f = float(val)
            return 0 if pd.isna(f) else int(f)
        except (TypeError, ValueError):
            return 0
