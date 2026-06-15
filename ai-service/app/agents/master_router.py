import json
import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict
import unicodedata

from app.agents.base_agent import BaseAgent
from app.agents.symbol_extractor import extract_symbols
from app.models.llm_factory import configured_providers_for_model_type, get_llm, LLMProvider

logger = logging.getLogger(__name__)

VALID_INTENTS = {
    "STOCK_OVERVIEW",
    "PORTFOLIO_RISK",
    "TRACKED_SYMBOLS",
    "PRICE_EXPLANATION",
    "CALCULATION",
    "CHARTING",
    "GREETING",
    "OUT_OF_SCOPE",
}

ROUTER_SYSTEM_PROMPT = """
You are an intent classifier for a Vietnamese stock market AI advisor.

Classify the user message into EXACTLY ONE of:
- STOCK_OVERVIEW: asks about a specific stock (price, fundamentals, news)
- PORTFOLIO_RISK: asks about their portfolio risk/performance
- TRACKED_SYMBOLS: asks which stocks/symbols the AI/system/user is tracking or following
- PRICE_EXPLANATION: asks why a price moved, news-driven analysis
- CALCULATION: asks for P&L, position sizing, financial math
- CHARTING: asks for a chart or visualization
- GREETING: greeting or small talk
- OUT_OF_SCOPE: not related to Vietnamese stock market

Also extract Vietnamese stock symbols (e.g. FPT, VIC, HPG, VHM, SSI).
Common Vietnamese exchanges: HOSE, HNX, UPCOM.

Respond ONLY with valid JSON:
{
  "intent": "<INTENT>",
  "symbols": ["<SYMBOL1>"],
  "requires_portfolio": <true|false>,
  "confidence": <0.0-1.0>,
  "reasoning": "<one sentence in Vietnamese>"
}
"""


@dataclass
class RouterDecision:
    """Structure for deterministic routing decisions."""
    intent: str
    symbols: list[str]
    requires_portfolio: bool = False


def configured_providers() -> list[LLMProvider]:
    """Get list of active LLM providers based on environment settings."""
    return configured_providers_for_model_type("routing")


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value or "")
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn").lower()


def has_phrase(value: str, phrases: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(phrase)}\b", value) for phrase in phrases)


@lru_cache(maxsize=1)
def supported_symbol_aliases() -> dict[str, list[str]]:
    aliases_path = Path(__file__).resolve().parents[1] / "data" / "symbol_aliases.json"
    try:
        raw = json.loads(aliases_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to load symbol aliases: %s", exc)
        raw = {"FPT": ["FPT"], "VIC": ["VIC"], "VNM": ["VNM"], "HPG": ["HPG"], "SSI": ["SSI"], "VHM": ["VHM"], "VND": ["VND"]}
    return {symbol.upper(): aliases for symbol, aliases in raw.items()}


def deterministic_symbols(message: str) -> list[str]:
    aliases = supported_symbol_aliases()
    normalized_message = normalize_text(message)
    symbols: set[str] = set()

    for token in re.findall(r"\b[a-zA-Z]{3}\b", message):
        symbol = token.upper()
        if symbol in aliases:
            symbols.add(symbol)

    for symbol, symbol_aliases in aliases.items():
        for alias in symbol_aliases:
            normalized_alias = normalize_text(alias)
            if normalized_alias and re.search(rf"\b{re.escape(normalized_alias)}\b", normalized_message):
                symbols.add(symbol)
                break

    return sorted(symbols)


def is_tracked_symbols_question(message: str) -> bool:
    msg = normalize_text(message)
    tracking_terms = [
        "track",
        "tracked",
        "tracking",
        "theo doi",
        "dang theo doi",
        "dang track",
    ]
    symbol_terms = [
        "co phieu",
        "ma",
        "ma nao",
        "symbol",
        "symbols",
        "ticker",
        "tickers",
    ]
    return any(term in msg for term in tracking_terms) and any(term in msg for term in symbol_terms)


def deterministic_route(message: str) -> RouterDecision:
    """Fallback rule-based router for Vietnam stock market intents."""
    msg = normalize_text(message)
    symbols = deterministic_symbols(message)

    # 2. Classify intent
    if is_tracked_symbols_question(message):
        intent = "TRACKED_SYMBOLS"
    elif has_phrase(msg, ["xin chao", "chao", "hello"]):
        intent = "GREETING"
    elif has_phrase(msg, ["bieu do", "chart"]) or re.search(r"\bve\s+(bieu do|chart)\b", msg):
        intent = "CHARTING"
    elif has_phrase(msg, ["lai lo", "pnl", "calculator", "tinh lai", "tinh lo", "loi nhuan", "phan tram lai"]):
        intent = "CALCULATION"
    elif has_phrase(msg, ["danh muc", "portfolio", "tai san"]):
        intent = "PORTFOLIO_RISK"
    elif has_phrase(msg, ["tai sao", "tin tuc", "news"]):
        intent = "PRICE_EXPLANATION"
    elif symbols:
        intent = "STOCK_OVERVIEW"
    else:
        intent = "OUT_OF_SCOPE"

    return RouterDecision(
        intent=intent,
        symbols=symbols,
        requires_portfolio=(intent == "PORTFOLIO_RISK"),
    )


class MasterRouterAgent(BaseAgent):
    """Router agent with LLM-powered intent classification.

    Classifies user intent and extracts stock symbols from the message.
    Falls back to deterministic rule-based router if LLM is unavailable.
    """

    @property
    def name(self) -> str:
        return "master_router"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Classify intent and extract symbols.

        Args:
            state: Current AdvisorState with user_message.

        Returns:
            State update with intent, symbols, requires_portfolio, and thoughts.
        """
        user_message = state.get("user_message", "")
        conversation_history = state.get("conversation_history", [])

        if is_tracked_symbols_question(user_message):
            return {
                "intent": "TRACKED_SYMBOLS",
                "symbols": [],
                "requires_portfolio": False,
                "thoughts": ["Router: Da nhan dien cau hoi ve danh sach ma dang theo doi."],
            }

        last_error = None
        for provider in configured_providers():
            try:
                llm = get_llm(provider=provider, temperature=0)
                # Retry loop to repair malformed JSON (runs twice)
                for attempt in range(2):
                    try:
                        messages = [("system", ROUTER_SYSTEM_PROMPT)]
                        for msg in conversation_history:
                            role = "human" if msg.get("role") == "user" else "ai"
                            messages.append((role, msg.get("content", "")))
                        messages.append(("human", user_message))

                        response = await llm.ainvoke(messages)
                        content = response.content.strip()
                        # Clean JSON codeblock wrappers if present
                        if content.startswith("```json"):
                            content = content[7:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()

                        parsed = json.loads(content)
                        intent = parsed.get("intent", "OUT_OF_SCOPE")
                        if intent not in VALID_INTENTS:
                            logger.warning("LLM returned unknown intent '%s'; defaulting to OUT_OF_SCOPE", intent)
                            intent = "OUT_OF_SCOPE"
                        llm_symbols = parsed.get("symbols", [])
                        if not isinstance(llm_symbols, list):
                            llm_symbols = []
                        llm_symbols = [str(symbol).upper() for symbol in llm_symbols if isinstance(symbol, str)]
                        llm_symbols = sorted(set([*llm_symbols, *deterministic_symbols(user_message)]))
                        if not llm_symbols and conversation_history:
                            for msg in reversed(conversation_history):
                                found = deterministic_symbols(msg.get("content", ""))
                                if found:
                                    llm_symbols = found
                                    break
                        requires_portfolio = parsed.get("requires_portfolio", False)

                        return {
                            "intent": intent,
                            "symbols": llm_symbols,
                            "requires_portfolio": requires_portfolio,
                            "thoughts": [f"Router: Đã phân loại intent={intent} dùng {provider.value}"],
                        }
                    except (json.JSONDecodeError, KeyError) as e:
                        last_error = e
                        logger.warning("JSON parse attempt %d failed for %s: %s", attempt + 1, provider.value, e)
                        continue
            except Exception as e:
                last_error = e
                logger.warning("LLM provider %s failed: %s", provider.value, e)
                continue

        # If all LLMs fail, fall back to deterministic routing
        logger.warning("All LLM providers failed, using deterministic fallback: %s", last_error)
        decision = deterministic_route(user_message)
        symbols = decision.symbols
        if not symbols and conversation_history:
            for msg in reversed(conversation_history):
                found = deterministic_symbols(msg.get("content", ""))
                if found:
                    symbols = found
                    break
        return {
            "intent": decision.intent,
            "symbols": symbols,
            "requires_portfolio": decision.requires_portfolio,
            "thoughts": ["Router: Phân loại thất bại, sử dụng fallback deterministic."],
        }
