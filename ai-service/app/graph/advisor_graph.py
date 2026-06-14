from typing import Any
from langgraph.graph import StateGraph, END
from app.graph.state import AdvisorState
from app.graph.nodes import (
    router_node,
    route_intent,
    context_planner_node,
    market_context_node,
    wiki_context_node,
    news_context_node,
    portfolio_context_node,
    tracked_symbols_node,
    calculation_node,
    chart_data_node,
    analyst_node,
    risk_manager_node,
    respond_node,
    safety_respond_node,
)


def create_advisor_graph(checkpointer: Any = None) -> Any:
    """Create and compile the AI Advisor LangGraph workflow.

    Flow:
    1. router -> classifies intent and extracts symbols.
    2. conditional edge:
       - GREETING/OUT_OF_SCOPE -> bypasses tools and goes to respond.
       - Analysis intents -> context_planner -> runs tools in parallel.
    3. Tool nodes execute parallel retrieval (market, wiki, news, etc.).
    4. Parallel tool results join at analyst node to generate the draft.
    5. Analyst output is passed to risk_manager to sanitize and apply policy.
    6. Conditional edge:
       - safe -> respond.
       - unsafe -> safety_respond (disclaimer/warnings).
    """
    workflow = StateGraph(AdvisorState)

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("context_planner", context_planner_node)
    workflow.add_node("market_context", market_context_node)
    workflow.add_node("wiki_context", wiki_context_node)
    workflow.add_node("news_context", news_context_node)
    workflow.add_node("portfolio_reader", portfolio_context_node)
    workflow.add_node("tracked_symbols_reader", tracked_symbols_node)
    workflow.add_node("calculation", calculation_node)
    workflow.add_node("chart_data", chart_data_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("risk_manager", risk_manager_node)
    workflow.add_node("respond", respond_node)
    workflow.add_node("safety_respond", safety_respond_node)

    # Set entry point
    workflow.set_entry_point("router")

    # Routing from router node
    workflow.add_conditional_edges(
        "router",
        route_intent,
        {
            "respond": "respond",
            "context_planner": "context_planner",
        },
    )

    # Parallel retrieval branches from context_planner to tools
    workflow.add_edge("context_planner", "market_context")
    workflow.add_edge("context_planner", "wiki_context")
    workflow.add_edge("context_planner", "news_context")
    workflow.add_edge("context_planner", "portfolio_reader")
    workflow.add_edge("context_planner", "tracked_symbols_reader")
    workflow.add_edge("context_planner", "calculation")
    workflow.add_edge("context_planner", "chart_data")

    # Joining parallel branches back at analyst node
    workflow.add_edge("market_context", "analyst")
    workflow.add_edge("wiki_context", "analyst")
    workflow.add_edge("news_context", "analyst")
    workflow.add_edge("portfolio_reader", "analyst")
    workflow.add_edge("tracked_symbols_reader", "analyst")
    workflow.add_edge("calculation", "analyst")
    workflow.add_edge("chart_data", "analyst")

    # Analyst results to risk_manager
    workflow.add_edge("analyst", "risk_manager")

    # Conditional routing after safety checks
    workflow.add_conditional_edges(
        "risk_manager",
        lambda state: "respond" if state.get("is_safe", True) else "safety_respond",
        {
            "respond": "respond",
            "safety_respond": "safety_respond",
        },
    )

    # Terminal edges
    workflow.add_edge("respond", END)
    workflow.add_edge("safety_respond", END)

    return workflow.compile(checkpointer=checkpointer)
