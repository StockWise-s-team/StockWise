from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class AnalystAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "analyst"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        analysis = (
            "Technical Analysis: RSI(14)=62 (neutral-bullish), "
            "MACD bullish crossover, "
            "Price above 50-day SMA, "
            "Volume 15% above 20-day average."
        )
        state["thoughts"] = state.get("thoughts", []) + [analysis]
        return state
