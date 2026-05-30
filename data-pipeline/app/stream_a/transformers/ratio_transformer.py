from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, InvalidOperation
from typing import List, Dict, Any, Optional
import logging

from app.shared.base_transformer import BaseTransformer
from app.stream_a.repositories.price_repository import NormalizedRatio

logger = logging.getLogger(__name__)

MAX_PE  = Decimal("1000")
MAX_PB  = Decimal("1000")
MAX_EPS = Decimal("100000")
MAX_ROE = Decimal("1")       # stored as decimal ratio, so max 1.0 = 100%
MAX_ROA = Decimal("1")

# Fields that must be numeric-positive (P/E, P/B, EPS must be >= 0)
RATIO_MUST_BE_POSITIVE = {"pe_ratio", "pb_ratio", "eps"}

# Fields that can be negative (loss-making company has negative EPS)
RATIO_CAN_BE_ANY = {"roe", "roa"}


class RatioTransformer(BaseTransformer):
    def transform(self, raw_data: Dict[str, Any]) -> List[NormalizedRatio]:
        symbol = self._normalize_symbol(raw_data.get("symbol", ""))
        ratios = raw_data.get("ratios", {})
        crawled_at = datetime.now(timezone.utc).isoformat()

        try:
            normalized = self._transform_ratios(symbol, ratios, crawled_at)
            logger.info(f"[RatioTransformer] Transformed ratios for {symbol}")
            return [normalized]
        except ValueError as e:
            logger.warning(
                f"[RatioTransformer] Skipped invalid ratios for {symbol}: {e}"
            )
            return []

    @staticmethod
    def _normalize_symbol(raw: str) -> str:
        return raw.strip().upper()

    @staticmethod
    def _parse_decimal(value: Any, field_name: str) -> Optional[Decimal]:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f"Invalid '{field_name}' value: {value}")

    def _validate_ratio(
        self, value: Optional[Decimal], field_name: str
    ) -> Optional[Decimal]:
        if value is None:
            return None

        upper_bound = self._get_upper_bound(field_name)
        if upper_bound is not None and abs(value) > upper_bound:
            raise ValueError(
                f"'{field_name}' out of range: {value} "
                f"(valid: {-upper_bound} to {upper_bound})"
            )
        return value

    @staticmethod
    def _get_upper_bound(field_name: str) -> Optional[Decimal]:
        bounds = {
            "pe_ratio": MAX_PE,
            "pb_ratio": MAX_PB,
            "eps": MAX_EPS,
            "roe": MAX_ROE,
            "roa": MAX_ROA,
        }
        return bounds.get(field_name)

    @staticmethod
    def _is_positive_required(field_name: str) -> bool:
        return field_name in RATIO_MUST_BE_POSITIVE

    def _transform_ratios(
        self, symbol: str, ratios: Dict[str, Any], crawled_at: str
    ) -> NormalizedRatio:
        period = ratios.get("period", "unknown")

        pe_ratio = self._parse_and_validate(ratios, "pe_ratio")
        pb_ratio = self._parse_and_validate(ratios, "pb_ratio")
        eps      = self._parse_and_validate(ratios, "eps")
        roe      = self._parse_and_validate(ratios, "roe")
        roa      = self._parse_and_validate(ratios, "roa")

        return NormalizedRatio(
            symbol=symbol,
            period=period,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            eps=eps,
            roe=roe,
            roa=roa,
        )

    def _parse_and_validate(self, ratios: Dict[str, Any], field: str) -> Optional[Decimal]:
        raw = ratios.get(field)
        value = self._parse_decimal(raw, field)
        value = self._validate_ratio(value, field)

        if value is not None and value < 0 and self._is_positive_required(field):
            raise ValueError(
                f"'{field}' must be non-negative, got {value}"
            )

        return value