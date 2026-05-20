import pytest

from app.graph.state import AdvisorState, ToolResult, PortfolioContext
from app.graph.advisor_graph import create_advisor_graph
from app.graph.graph_config import get_advisor_graph, get_graph_config


class TestAdvisorState:
    """Unit tests for AdvisorState structure."""

    def test_state_has_required_keys(self):
        """AdvisorState contains all required fields."""
        state: AdvisorState = {
            "user_message": "test",
            "user_id": "user-1",
            "session_id": "session-1",
            "conversation_history": [],
            "intent": "",
            "symbols": [],
            "requires_portfolio": False,
            "tool_results": [],
            "portfolio_context": None,
            "thoughts": [],
            "streaming_tokens": [],
            "risk_flags": [],
            "is_safe": True,
            "final_answer": "",
            "citations": [],
            "error": None,
        }
        assert state["user_message"] == "test"
        assert state["intent"] == ""

    def test_tool_result_structure(self):
        """ToolResult has correct structure."""
        result: ToolResult = {
            "tool_name": "wiki_reader",
            "tool_input": {"symbol": "FPT"},
            "tool_output": {"data": "test"},
            "success": True,
            "error": None,
        }
        assert result["tool_name"] == "wiki_reader"
        assert result["success"] is True

    def test_portfolio_context_structure(self):
        """PortfolioContext has correct structure."""
        ctx: PortfolioContext = {
            "user_id": "user-1",
            "holdings": [{"symbol": "FPT", "quantity": 100}],
            "total_value": 10000000.0,
            "unrealized_pnl": 500000.0,
            "fetched_at": "2026-01-01T00:00:00",
        }
        assert ctx["total_value"] == 10000000.0


class TestAdvisorGraph:
    """Unit tests for LangGraph workflow compilation."""

    def test_graph_compiles(self):
        """Graph compiles without errors."""
        graph = create_advisor_graph()
        assert graph is not None

    def test_graph_has_required_nodes(self):
        """Graph contains all expected nodes."""
        graph = create_advisor_graph()
        nodes = list(graph.get_graph().nodes.keys())
        assert "router" in nodes
        assert "analyst" in nodes
        assert "risk_manager" in nodes
        assert "respond" in nodes
        assert "safety_respond" in nodes

    def test_graph_singleton(self):
        """get_advisor_graph returns the same instance."""
        g1 = get_advisor_graph()
        g2 = get_advisor_graph()
        assert g1 is g2

    def test_graph_config(self):
        """get_graph_config returns correct thread_id config."""
        config = get_graph_config("test-session-123")
        assert config["configurable"]["thread_id"] == "test-session-123"

    def test_risk_manager_default_safe(self):
        """Risk manager node defaults to is_safe=True."""
        from app.graph.advisor_graph import risk_manager_node
        import asyncio

        state = {
            "user_message": "test",
            "user_id": "user-1",
            "session_id": "session-1",
            "conversation_history": [],
            "intent": "STOCK_OVERVIEW",
            "symbols": ["FPT"],
            "requires_portfolio": False,
            "tool_results": [],
            "portfolio_context": None,
            "thoughts": [],
            "streaming_tokens": [],
            "risk_flags": [],
            "is_safe": True,
            "final_answer": "",
            "citations": [],
            "error": None,
        }
        result = asyncio.get_event_loop().run_until_complete(risk_manager_node(state))
        assert result["is_safe"] is True
