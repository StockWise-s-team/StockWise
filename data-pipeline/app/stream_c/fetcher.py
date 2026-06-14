"""
stream_c / fetcher.py
=====================
Lấy giá real-time theo batch dùng vnstock.Trading.price_board().
Khác với VnStockFetcher (lịch sử 30 ngày), PriceBoardFetcher lấy snapshot
hiện tại của toàn bộ danh sách symbol cùng một lần gọi.

Cấu trúc trả về mỗi phần tử:
    {
        "symbol": str,
        "close":  float,          # giá khớp lệnh mới nhất (hoặc close)
        "open":   float,
        "high":   float,
        "low":    float,
        "volume": int,            # khối lượng tích lũy trong ngày
        "reference_price": float, # giá tham chiếu (TC)
        "price_change":   float,  # thay đổi tuyệt đối
        "percent_change": float,  # thay đổi %
        "timestamp": str,         # ISO UTC
    }
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

# Kích thước batch mỗi lần gọi price_board
# vnstock KBS chịu khoảng 50 symbols/lần — giữ 40 để an toàn
BATCH_SIZE = 40
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10


class PriceBoardFetcher:
    """Lấy snapshot giá hiện tại cho nhiều symbols cùng lúc."""

    @property
    def source_name(self) -> str:
        return "vnstock_price_board"

    async def fetch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch giá real-time cho list symbols.
        Tự chia batch để không quá tải API.
        """
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
                    "[PriceBoardFetcher] Batch failed for %s: %s: %s",
                    batch,
                    type(e).__name__,
                    e,
                )
                # Trả về dữ liệu lỗi cho từng symbol trong batch
                for sym in batch:
                    results.append({"symbol": sym, "error": str(e)})

        return results

    async def _fetch_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                df = await asyncio.to_thread(self._call_price_board, symbols)
                return self._df_to_records(df)
            except Exception as e:
                err_msg = str(e).lower()
                is_rate_limit = any(
                    k in err_msg for k in ("rate limit", "giới hạn api", "request limit")
                )
                logger.warning(
                    "[PriceBoardFetcher] attempt %d/%d failed%s: %s",
                    attempt,
                    MAX_RETRIES,
                    " (rate limit)" if is_rate_limit else "",
                    e,
                )
                if attempt < MAX_RETRIES:
                    delay = 60 if is_rate_limit else RETRY_DELAY_SECONDS * attempt
                    await asyncio.sleep(delay)
                else:
                    raise

        raise RuntimeError("Unreachable")

    @staticmethod
    def _call_price_board(symbols: List[str]) -> pd.DataFrame:
        import vnstock

        vnstock.config.API_KEY = settings.VNSTOCK_API_KEY or ""
        trading = vnstock.Trading(source="kbs")
        return trading.price_board(symbols_list=symbols)

    @staticmethod
    def _df_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Chuẩn hóa DataFrame từ price_board thành list dict."""
        if df is None or df.empty:
            return []

        now_iso = datetime.now(timezone.utc).isoformat()
        records: List[Dict[str, Any]] = []

        # Cột bắt buộc từ kết quả test:
        # symbol, close_price, open_price, high_price, low_price,
        # volume_accumulated, reference_price, price_change, percent_change
        col_map = {
            "close_price": "close",
            "open_price": "open",
            "high_price": "high",
            "low_price": "low",
            "volume_accumulated": "volume",
            "reference_price": "reference_price",
            "price_change": "price_change",
            "percent_change": "percent_change",
            "average_price": "average_price",
            "ceiling_price": "ceiling_price",
            "floor_price": "floor_price",
        }

        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        def safe(val, cast=float, default=None):
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return default
            try:
                return cast(val)
            except (TypeError, ValueError):
                return default

        for _, row in df.iterrows():
            sym = str(row.get("symbol", "")).strip().upper()
            if not sym:
                continue

            close = safe(row.get("close"))
            if close is None:
                continue  # bỏ qua nếu không có giá

            record: Dict[str, Any] = {
                "symbol": sym,
                "close": close,
                "open": safe(row.get("open")),
                "high": safe(row.get("high")),
                "low": safe(row.get("low")),
                "volume": safe(row.get("volume"), cast=int, default=0),
                "reference_price": safe(row.get("reference_price")),
                "price_change": safe(row.get("price_change")),
                "percent_change": safe(row.get("percent_change")),
                "average_price": safe(row.get("average_price")),
                "ceiling_price": safe(row.get("ceiling_price")),
                "floor_price": safe(row.get("floor_price")),
                "timestamp": now_iso,
            }
            records.append(record)

        return records
