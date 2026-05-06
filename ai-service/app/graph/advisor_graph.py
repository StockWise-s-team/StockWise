from typing import TypedDict, List, Annotated, Dict, Any
import operator
from langgraph.graph import StateGraph, END


class AdvisorState(TypedDict):
    messages: Annotated[List[str], operator.add]
    intent: str
    thoughts: Annotated[List[str], operator.add]
    final_answer: str


async def router_node(state: AdvisorState) -> Dict[str, Any]:
    return {
        "intent": "analysis",
        "thoughts": ["Router: Analyzing intent -> technical analysis requested."],
    }


async def route_intent(state: AdvisorState) -> str:
    intent = state.get("intent", "")
    if intent == "analysis":
        return "analysis"
    return "respond"


async def analyst_node(state: AdvisorState) -> Dict[str, Any]:
    return {
        "thoughts": ["Analyst: Running technical analysis. RSI(14)=62, MACD bullish crossover detected."],
    }


async def risk_manager_node(state: AdvisorState) -> Dict[str, Any]:
    return {
        "thoughts": ["Risk Manager: Risk review passed. Moderate risk profile. Consider 5% stop-loss."],
    }


async def respond_node(state: AdvisorState) -> Dict[str, Any]:
    thoughts = state.get("thoughts", [])
    return {
        "final_answer": (
            "I've analyzed your query. The current technical indicators show bullish momentum "
            "with RSI at 62 and a MACD bullish crossover. Risk assessment rates this as moderate. "
            "Consider a stop-loss at 5% below current price."
        ),
        "thoughts": thoughts + ["Respond: Compiling final answer."],
    }


def create_advisor_graph():
    workflow = StateGraph(AdvisorState)
    workflow.add_node("router", router_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("risk_manager", risk_manager_node)
    workflow.add_node("respond", respond_node)
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        route_intent,
        {"analysis": "analyst", "respond": "respond"},
    )
    workflow.add_edge("analyst", "risk_manager")
    workflow.add_edge("risk_manager", "respond")
    workflow.add_edge("respond", END)
    return workflow.compile()
