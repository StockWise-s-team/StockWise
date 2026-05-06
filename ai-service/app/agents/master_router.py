from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class MasterRouterAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "master_router"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["intent"] = "analysis"
        state["thoughts"] = state.get("thoughts", []) + ["MasterRouter: Routing to technical analysis agent."]
        return state
