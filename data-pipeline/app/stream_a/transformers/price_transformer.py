from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any
import logging

from app.shared.base_transformer import BaseTransformer
from app.stream_a.repositories.price_repository import NormalizedPrice

logger = logging.getLogger(__name__)

MAX_PRICE = Decimal("1000000")    # Giá cổ phiếu VN không quá 1 triệu
MIN_PRICE = Decimal("0.001")     # Giá tối thiểu hợp lệ

class PriceTransformer(BaseTransformer):
    def transform(self, raw_data: Dict[str, Any]) -> List[NormalizedPrice]:
        symbol = self._normalize_symbol(raw_data.get("symbol", ""))
        bars = raw_data.get("prices", [])
        results: List[NormalizedPrice] = []

        for bar in bars:
            try:
                normalized = self._transform_bar(symbol, bar)
                results.append(normalized)
            except ValueError as e:
                logger.warning(
                    f"[PriceTransformer] Skipped invalid bar for {symbol}: {e}"
                )

        logger.info(
            f"[PriceTransformer] Transformed {len(results)}/{len(bars)} bars "
            f"for {symbol}"
        )
        return results
    
    @staticmethod
    def _normalize_symbol(raw: str) -> str:
        return raw.strip().upper()   
    
    @staticmethod
    def _parse_volume(value: Any) -> int:
        if value is None:
            return 0
        try:
            v = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid volume value: {value}")
        if v < 0:
            raise ValueError(f"Volume cannot be negative: {v}")
        return v
    
    @staticmethod
    def _validate_ohlc(high, low, open_, close) -> None:
        if high < low:
            raise ValueError(
                f"High ({high}) must be >= Low ({low})"
            )
        if high < open_:
            raise ValueError(
                f"High ({high}) must be >= Open ({open_})"
            )
        if high < close:
            raise ValueError(
                f"High ({high}) must be >= Close ({close})"
            )
        if low > open_:
            raise ValueError(
                f"Low ({low}) must be <= Open ({open_})"
            )
        if low > close:
            raise ValueError(
                f"Low ({low}) must be <= Close ({close})"
            )
    
    def _parse_price(self, value: Any, field_name: str) -> Decimal:
        if value is None:
            raise ValueError(f"Missing '{field_name}'")
        try:
            price = Decimal(str(value))
        except (InvalidOperation, TypeError):
            raise ValueError(f"Invalid '{field_name}' value: {value}")
        if price < MIN_PRICE or price > MAX_PRICE:
            raise ValueError(
                f"'{field_name}' out of range: {price} "
                f"(valid: {MIN_PRICE}–{MAX_PRICE})"
            )
        return price

    def _transform_bar(self, symbol: str, bar: Dict[str, Any], crawled_at: str) -> NormalizedPrice:
        # Parse date
        date_str = bar.get("date")
        if not date_str:
            raise ValueError(f"Missing 'date' in bar")
        # Parse numeric fields với Decimal (tránh float error)
        price_open  = self._parse_price(bar.get("open"), "open")
        price_high  = self._parse_price(bar.get("high"), "high")
        price_low   = self._parse_price(bar.get("low"),  "low")
        price_close = self._parse_price(bar.get("close"), "close")
        volume      = self._parse_volume(bar.get("volume"))
        # Validate OHLC logic
        self._validate_ohlc(price_high, price_low, price_open, price_close)
        return NormalizedPrice(
            symbol=symbol,
            trade_date=date_str,
            open=price_open,
            high=price_high,
            low=price_low,
            close=price_close,
            volume=volume,
        )