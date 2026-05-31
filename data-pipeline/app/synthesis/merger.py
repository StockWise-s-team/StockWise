import json
import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.synthesis.exceptions import (
    GeminiParseError,
    GeminiRateLimitError,
    SynthesisError,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
_RETRYABLE_STATUS_CODES = {429, 503}

_WIKI_REQUIRED_FIELDS = frozenset({
    "company_name",
    "sector",
    "business_summary",
    "recent_performance",
    "key_risks",
    "sentiment",
    "last_news_summary",
    "financials_snapshot",
    "version",
})

class Merger:
    _DEFAULT_WIKI: Dict[str, Any] = {
        "symbol": "UNKNOWN",
        "company_name": "Unknown Company",
        "sector": "Unknown",
        "business_summary": "",
        "recent_performance": {"trend": "neutral", "notable": ""},
        "key_risks": [],
        "sentiment": "neutral",
        "last_news_summary": "",
        "financials_snapshot": {"pe": 0, "pb": 0, "roe": 0},
        "version": 1,
    }

    def __init__(self, wiki_repo=None):
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self._wiki_repo = wiki_repo

    async def merge(
        self,
        old_wiki: Dict[str, Any],
        new_articles: List[Dict[str, Any]],
        new_price_data: List[Dict[str, Any]],
        symbol: str,
    ) -> Dict[str, Any]:
        effective_wiki = old_wiki if old_wiki else dict(self._DEFAULT_WIKI)
        effective_wiki["symbol"] = symbol

        # Fetch authoritative company metadata from DB (populated by FMP API)
        if effective_wiki.get("company_name") in ("Unknown Company", "", None):
            if self._wiki_repo:
                try:
                    db_info = self._wiki_repo.get_company_info(symbol)
                    if db_info:
                        effective_wiki["company_name"] = db_info.get("company_name") or symbol
                        effective_wiki["sector"] = db_info.get("sector") or "Unknown"
                        effective_wiki["business_summary"] = db_info.get("business_summary") or ""
                except Exception:
                    pass  # non-fatal — fall back to defaults

        # Enrich with actual financial ratios from DB
        ratios = None
        if self._wiki_repo:
            try:
                ratios = self._wiki_repo.get_ratios(symbol)
            except Exception:
                pass  # non-fatal — ratios are optional

        user_prompt = self._build_user_prompt(effective_wiki, new_articles, new_price_data, ratios)
        response_text = await self._call_llm(user_prompt)
        parsed = self._parse_response(response_text)
        parsed["symbol"] = symbol

        # Always override with authoritative company info from DB (FMP API)
        if self._wiki_repo:
            try:
                db_info = self._wiki_repo.get_company_info(symbol)
                if db_info:
                    parsed["company_name"] = db_info.get("company_name") or symbol
                    parsed["sector"] = db_info.get("sector") or "Unknown"
                    parsed["business_summary"] = db_info.get("business_summary") or ""
            except Exception:
                pass

        # Always override financials_snapshot with real DB ratios
        if ratios:
            parsed["financials_snapshot"] = {
                "pe": ratios.get("pe_ratio", 0),
                "pb": ratios.get("pb_ratio", 0),
                "roe": ratios.get("roe", 0),
            }

        return parsed

    def _build_user_prompt(
        self,
        old_wiki: Dict[str, Any],
        new_articles: List[Dict[str, Any]],
        new_price_data: List[Dict[str, Any]],
        ratios: Optional[Dict[str, Any]] = None,
    ) -> str:
        from app.synthesis.prompts import MERGE_USER_PROMPT

        wiki_json = json.dumps(old_wiki, ensure_ascii=False, default=str)
        articles_json = json.dumps(
            [
                {
                    "title": a.get("title", ""),
                    "content": a.get("content", ""),
                    "published_at": str(a.get("published_at", "")),
                }
                for a in new_articles
            ],
            ensure_ascii=False,
            default=str,
        )
        prices_json = json.dumps(
            [
                {
                    "trade_date": str(p.get("trade_date", "")),
                    "close": str(p.get("close", "")),
                    "volume": p.get("volume", 0),
                }
                for p in new_price_data
            ],
            ensure_ascii=False,
            default=str,
        )
        ratios_json = json.dumps(ratios, ensure_ascii=False, default=str) if ratios else "N/A"
        return MERGE_USER_PROMPT.format(
            old_wiki=wiki_json,
            new_articles=articles_json,
            new_price_data=prices_json,
            financial_ratios=ratios_json,
        )

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(GeminiRateLimitError),
        reraise=True,
    )
    async def _call_llm(self, prompt: str) -> str:
        from app.synthesis.prompts import MERGE_SYSTEM_PROMPT

        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENAI_LLM_MODEL,
                messages=[
                    {"role": "system", "content": MERGE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return content or "{}"
        except Exception as exc:
            error_str = str(exc).lower()
            status_code = getattr(exc, "status_code", None)
            is_rate_limit = (
                status_code in _RETRYABLE_STATUS_CODES
                or "429" in error_str
                or "rate_limit" in error_str
                or "quota" in error_str
                or "too many requests" in error_str
            )
            if is_rate_limit:
                logger.warning("[Merger] LLM rate limit hit: %s", exc)
                raise GeminiRateLimitError(str(exc)) from exc
            logger.error("[Merger] LLM call failed: %s", exc)
            raise SynthesisError(f"LLM call failed: {exc}") from exc

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        try:
            data = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            logger.error("[Merger] Invalid JSON from LLM for %s: %s", symbol, e)
            raise GeminiParseError(f"Invalid JSON for {symbol}: {e}") from e

        if not isinstance(data, dict):
            raise GeminiParseError(
                f"Expected JSON object for {symbol}, got {type(data).__name__}"
            )

        missing = _WIKI_REQUIRED_FIELDS - set(data.keys())
        if missing:
            logger.warning(
                "[Merger] Missing required fields in LLM response: %s", missing
            )
            for field in missing:
                data.setdefault(field, self._DEFAULT_WIKI.get(field))

        return data
