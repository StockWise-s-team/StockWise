from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class RiskManagerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "risk_manager"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        review = "Risk Review: Moderate risk profile. Diversification adequate. Stop-loss recommended at 5% below entry."
        state["thoughts"] = state.get("thoughts", []) + [review]
        return state
