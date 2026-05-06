from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class SynthesisAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "synthesis"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        synthesis = "Synthesis: Aggregated 5 news articles into consolidated wiki update."
        state["thoughts"] = state.get("thoughts", []) + [synthesis]
        return state
