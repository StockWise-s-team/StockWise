import pytest

from app.graph.advisor_graph import create_advisor_graph
from app.models.schemas import ToolResult


class FakeRuntime:
    def __init__(self):
        self.calls = []

    async def validate_symbols(self, candidates):
        return candidates

    async def execute_tool(self, tool_name, state):
        self.calls.append(tool_name)
        return ToolResult(tool_name=tool_name, success=True)

    async def generate_answer(self, state):
        return "grounded draft"

    def sanitize_answer(self, state):
        return {
            "final_answer": state["final_answer"],
            "risk_flags": [],
            "is_safe": True,
            "has_disclaimer": True,
            "citations": [],
            "data_freshness": {},
            "data_mode": "live",
            "thoughts": ["safe"],
        }


def initial_state():
    return {
        "user_message": "Phan tich FPT",
        "user_id": "user-1",
        "session_id": "session-1",
        "conversation_history": [],
        "intent": "",
        "symbols": [],
        "requested_symbols": [],
        "requires_portfolio": False,
        "planned_tools": [],
        "tool_results": [],
        "portfolio_context": None,
        "thoughts": [],
        "streaming_tokens": [],
        "risk_flags": [],
        "is_safe": True,
        "has_disclaimer": False,
        "final_answer": "",
        "citations": [],
        "data_mode": "live",
        "data_freshness": {},
        "error": None,
    }


@pytest.mark.asyncio
async def test_stock_overview_graph_calls_each_planned_tool_once():
    runtime = FakeRuntime()
    result = await create_advisor_graph().ainvoke(
        initial_state(),
        config={"configurable": {"runtime": runtime}},
    )
    assert sorted(runtime.calls) == sorted(["market_data", "wiki_reader", "news_search"])
    assert result["final_answer"] == "grounded draft"
