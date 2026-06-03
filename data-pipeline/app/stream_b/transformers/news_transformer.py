import re
import uuid
import logging
from datetime import datetime, timezone
from typing import Any

import psycopg2
from bs4 import BeautifulSoup

from app.config import settings
from app.sources.models import NewsSource
from app.shared.ticker_validator import is_valid_ticker
from app.stream_b.exceptions import SourceMapError, TransformError
from app.stream_b.repositories.news_repository import NewsRepository, NormalizedArticle
from app.shared.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)

STOCK_SYMBOL_RE = re.compile(
    r"\b([A-Z]{3,4})(?:\.VN|:[a-z]+)?\b"
)

VN_KEYWORDS = {
    "vietnam", "viet nam", "vn-index", "vnindex",
    "hnx", "upcom", "hsx", "hose",
}

VN_SYMBOL_RE = re.compile(
    r"\b(VN30|VN100|VNAll|Nickel|VNDirect|VietinBank|"
    r"[A-Z]{3,4})\b",
    re.IGNORECASE,
)

ARTICLES_PER_SYMBOL_RE = re.compile(
    r"article[s]?\s+(?:for|mentioning)\s+([A-Z]{3,4})",
    re.IGNORECASE,
)

# Currency/cash flow codes that appear as 3-char caps but are not stock tickers
# and sometimes slip through the valid_tickers filter.
CURRENCY_CODES = {"USD", "VND", "EUR", "GBP", "JPY", "CNY", "SGD", "THB", "AUD", "CAD"}


def _strip_html_static(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s{2,}", " ", text)


class NewsTransformer(BaseTransformer):
    def __init__(self):
        self._source_cache: dict[str, uuid.UUID] = {}
        self._news_repo = NewsRepository()

    def transform(self, raw_data: Any) -> dict[str, Any]:
        if isinstance(raw_data, list):
            return [t for item in raw_data if (t := self._transform_one(item)) is not None]
        result = self._transform_one(raw_data)
        return result if result is not None else []

    def _transform_one(self, raw: dict[str, Any]) -> NormalizedArticle | None:
        try:
            content_clean = self._strip_html(raw.get("content", ""))
            symbols = self._extract_symbols_from_raw(raw)
            if not symbols:
                logger.info(
                    "[NewsTransformer] Skipping article (no symbols): %s",
                    raw.get("title", "")[:60],
                )
                return None
            source_name = raw.get("source_name", "")
            source_id = self._resolve_source_id(source_name)
            crawled_at = datetime.now(timezone.utc)

            published_at = self._parse_published_at(raw.get("published_at"))

            return NormalizedArticle(
                source_id=str(source_id),
                title=raw.get("title", "").strip(),
                content=content_clean,
                url=raw.get("url", "").strip(),
                symbols=symbols,
                published_at=published_at,
                crawled_at=crawled_at,
            )
        except Exception as exc:
            raise TransformError(
                raw.get("source_name", "unknown"), str(exc)
            ) from exc

    @staticmethod
    def _strip_html(html: str) -> str:
        return _strip_html_static(html)

    @staticmethod
    def _extract_symbols(text: str) -> list[str]:
        raw = STOCK_SYMBOL_RE.findall(text.upper())
        seen: set[str] = set()
        symbols: list[str] = []

        for sym in raw:
            if sym in seen:
                continue
            # Priority: valid_tickers.json overrides CURRENCY_CODES exclusion.
            # VND is a valid stock ticker (VNDIRECT Securities) and must NOT
            # be filtered out by the currency-code exclusion.
            if is_valid_ticker(sym):
                seen.add(sym)
                symbols.append(sym)
                continue
            if sym in CURRENCY_CODES:
                continue
            if sym in {
                "THE", "AND", "FOR", "THIS", "THAT", "WITH", "FROM",
                "HAVE", "HAS", "NOT", "ARE", "WERE", "VNINDEX",
                "VN30", "VN100", "HNX", "HSX", "HOSE", "UPCAM",
                "HERE", "WHEN", "SUCH", "MORE", "THAN", "THEN",
                "CHIA", "THU", "MUA", "THEO", "QUAN", "SAU", "GIAO",
                "KINH", "CHO", "KHI", "NGAY", "BAO", "NAY", "HAI",
                "QUY", "NAM", "CAO", "DUY", "THAY", "HCM", "TIN",
            }:
                continue
            seen.add(sym)
            symbols.append(sym)

        return symbols

    @staticmethod
    def _extract_symbols_from_raw(raw: dict[str, Any]) -> list[str]:
        """
        Extract symbols with priority:
        1. Use symbols directly from crawler (preferred for API-driven crawlers
           like Cafef that return pre-tagged symbols via linkStocks field).
        2. Fall back to regex extraction from text.
        """
        direct = raw.get("symbols")
        if direct and isinstance(direct, list) and len(direct) > 0:
            validated = [s.upper() for s in direct if is_valid_ticker(s.upper())]
            if validated:
                return validated

        content_clean = _strip_html_static(raw.get("content", ""))
        text = f"{raw.get('title', '')} {raw.get('excerpt', '')} {content_clean}"
        return NewsTransformer._extract_symbols(text)

    def _resolve_source_id(self, source_name: str) -> uuid.UUID:
        if source_name in self._source_cache:
            return self._source_cache[source_name]

        conn = self._news_repo.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM news_sources WHERE crawler_type = %s LIMIT 1",
                    (source_name,),
                )
                row = cur.fetchone()
        finally:
            conn.close()

        if row is None:
            raise SourceMapError(source_name)

        source_id: uuid.UUID = row[0]
        self._source_cache[source_name] = source_id
        return source_id

    @staticmethod
    def _parse_published_at(value: Any) -> datetime | None:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass
        return None
