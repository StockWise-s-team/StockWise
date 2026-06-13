import json
import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.synthesis.exceptions import (
    LLMParseError,
    LLMRateLimitError,
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

        # Fetch authoritative company metadata from DB (populated by VnStock/VCI API)
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
        parsed = self._parse_response(response_text, symbol)
        parsed["symbol"] = symbol

        # Always override with authoritative company info from DB (VnStock/VCI API)
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
        retry=retry_if_exception_type(LLMRateLimitError),
        reraise=True,
    )
    async def _call_llm(self, prompt: str) -> str:
        from app.synthesis.prompts import MERGE_SYSTEM_PROMPT

        models = [settings.DATA_WIKI_PRIMARY_MODEL, settings.DATA_WIKI_FALLBACK_MODEL]
        last_exception = None

        for model_name in models:
            if not model_name:
                continue
            try:
                if "gemini" in model_name.lower() and settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key":
                    import google.generativeai as genai
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=MERGE_SYSTEM_PROMPT
                    )
                    response = await model.generate_content_async(
                        prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    content = response.text
                    return content or "{}"
                else:
                    response = await self._client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": MERGE_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        response_format={"type": "json_object"},
                    )
                    content = response.choices[0].message.content
                    return content or "{}"
            except Exception as exc:
                last_exception = exc
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
                    logger.warning("[Merger] LLM model %s rate limit hit: %s", model_name, exc)
                    continue
                logger.error("[Merger] LLM model %s failed: %s", model_name, exc)
                continue

        # If all models failed
        if last_exception:
            error_str = str(last_exception).lower()
            status_code = getattr(last_exception, "status_code", None)
            is_rate_limit = (
                status_code in _RETRYABLE_STATUS_CODES
                or "429" in error_str
                or "rate_limit" in error_str
                or "quota" in error_str
                or "too many requests" in error_str
            )
            if is_rate_limit:
                raise LLMRateLimitError(str(last_exception)) from last_exception
            raise SynthesisError(f"All LLM models failed. Last error: {last_exception}") from last_exception
        
        raise SynthesisError("All LLM models failed.")

    def _parse_response(self, response_text: str, symbol: str) -> Dict[str, Any]:
        try:
            data = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            logger.error("[Merger] Invalid JSON from LLM for %s: %s", symbol, e)
            raise LLMParseError(f"Invalid JSON for {symbol}: {e}") from e

        if not isinstance(data, dict):
                raise LLMParseError(
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
