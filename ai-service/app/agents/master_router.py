import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.agents.symbol_extractor import extract_symbols
from app.models.llm_factory import configured_providers_for_model_type, get_llm, LLMProvider

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """
You are an intent classifier for a Vietnamese stock market AI advisor.

Classify the user message into EXACTLY ONE of:
- STOCK_OVERVIEW: asks about a specific stock (price, fundamentals, news)
- PORTFOLIO_RISK: asks about their portfolio risk/performance
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


def deterministic_route(message: str) -> RouterDecision:
    """Fallback rule-based router for Vietnam stock market intents."""
    msg = message.lower()
    
    # 1. Extract symbol (3-letter uppercase symbols)
    symbols = []
    for token in re.findall(r"\b[a-zA-Z]{3}\b", message):
        symbols.append(token.upper())
        
    # 2. Classify intent
    if "xin chao" in msg or "chao" in msg or "hello" in msg or msg.strip() == "xin chao":
        intent = "GREETING"
    elif "bieu do" in msg or "chart" in msg or "ve" in msg:
        intent = "CHARTING"
    elif "lai lo" in msg or "tinh" in msg or "pnl" in msg or "calculator" in msg:
        intent = "CALCULATION"
    elif "danh muc" in msg or "portfolio" in msg or "tai san" in msg:
        intent = "PORTFOLIO_RISK"
    elif "tai sao" in msg or "tin tuc" in msg or "news" in msg:
        intent = "PRICE_EXPLANATION"
    elif any(sym.lower() in msg for sym in ["fpt", "vic", "vnm", "hpg", "ssi", "vhm", "vnd"]):
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

        last_error = None
        for provider in configured_providers():
            try:
                llm = get_llm(provider=provider, temperature=0)
                # Retry loop to repair malformed JSON (runs twice)
                for attempt in range(2):
                    try:
                        response = await llm.ainvoke([
                            ("system", ROUTER_SYSTEM_PROMPT),
                            ("human", user_message),
                        ])
                        content = response.content.strip()
                        # Clean JSON codeblock wrappers if present
                        if content.startswith("```json"):
                            content = content[7:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()
                        
                        parsed = json.loads(content)
                        intent = parsed.get("intent", "OUT_OF_SCOPE")
                        llm_symbols = parsed.get("symbols", [])
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
        return {
            "intent": decision.intent,
            "symbols": decision.symbols,
            "requires_portfolio": decision.requires_portfolio,
            "thoughts": ["Router: Phân loại thất bại, sử dụng fallback deterministic."],
        }
