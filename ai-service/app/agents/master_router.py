import json
import logging
from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.agents.symbol_extractor import extract_symbols
from app.models.llm_factory import get_llm
from app.config import settings

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


class MasterRouterAgent(BaseAgent):
    """Router agent with LLM-powered intent classification.

    Classifies user intent and extracts stock symbols from the message.
    Falls back to OUT_OF_SCOPE if LLM is unavailable.
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

        try:
            llm = get_llm(temperature=0)
            response = await llm.ainvoke([
                ("system", ROUTER_SYSTEM_PROMPT),
                ("human", user_message),
            ])

            content = response.content.strip()
            parsed = json.loads(content)

            intent = parsed.get("intent", "OUT_OF_SCOPE")
            llm_symbols = parsed.get("symbols", [])
            requires_portfolio = parsed.get("requires_portfolio", False)

            return {
                "intent": intent,
                "symbols": llm_symbols,
                "requires_portfolio": requires_portfolio,
                "thoughts": [f"Router: Đã phân loại intent={intent}"],
            }

        except Exception as e:
            logger.warning("LLM classification failed, using fallback: %s", str(e))
            return {
                "intent": "OUT_OF_SCOPE",
                "symbols": [],
                "requires_portfolio": False,
                "thoughts": ["Router: Không thể phân loại, sử dụng fallback."],
            }
