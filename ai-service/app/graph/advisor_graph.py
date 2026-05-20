from typing import Any, Dict

from langgraph.graph import StateGraph, END

from app.agents.master_router import MasterRouterAgent
from app.agents.symbol_extractor import extract_symbols
from app.db.database import AsyncSessionLocal
from app.graph.state import AdvisorState


async def router_node(state: AdvisorState) -> Dict[str, Any]:
    """Classify user intent and extract symbols using LLM + regex.

    Uses MasterRouterAgent for LLM classification, then validates
    symbols against the database.
    """
    agent = MasterRouterAgent()
    result = await agent.run(state)

    symbols = result.get("symbols", [])
    if symbols:
        async with AsyncSessionLocal() as session:
            validated = await extract_symbols(state["user_message"], session)
            if validated:
                result["symbols"] = validated

    return result


async def route_intent(state: AdvisorState) -> str:
    """Determine next node based on intent classification."""
    intent = state.get("intent", "")
    if intent in ("GREETING", "OUT_OF_SCOPE"):
        return "respond"
    return "analyst"


async def analyst_node(state: AdvisorState) -> Dict[str, Any]:
    """Synthesize answer from tool results and portfolio context.

    This node will be enhanced with real LLM streaming in Phase 3.
    """
    return {
        "thoughts": ["Analyst: Đang tổng hợp thông tin..."],
    }


async def risk_manager_node(state: AdvisorState) -> Dict[str, Any]:
    """Check response for safety compliance.

    This node will be enhanced with real safety rules in Phase 3.
    """
    return {
        "thoughts": ["Risk Manager: Đang kiểm tra an toàn..."],
        "risk_flags": [],
        "is_safe": True,
    }


async def respond_node(state: AdvisorState) -> Dict[str, Any]:
    """Format final answer with citations."""
    thoughts = state.get("thoughts", [])
    return {
        "final_answer": (
            "Cảm ơn bạn đã sử dụng StockWise AI Advisor. "
            "Hệ thống đang được nâng cấp để cung cấp phân tích chi tiết hơn. "
            "Vui lòng thử lại sau."
        ),
        "thoughts": thoughts + ["Respond: Đang chuẩn bị câu trả lời..."],
        "citations": [],
    }


async def safety_respond_node(state: AdvisorState) -> Dict[str, Any]:
    """Format response with mandatory risk disclaimer."""
    return {
        "final_answer": (
            "⚠️ **Lưu ý quan trọng:** Thông tin trên chỉ mang tính tham khảo và KHÔNG phải là lời khuyên "
            "đầu tư. Đầu tư chứng khoán có rủi ro, bạn có thể mất một phần hoặc toàn bộ vốn. "
            "Hãy tham khảo chuyên gia tài chính được cấp phép trước khi đưa ra quyết định đầu tư."
        ),
        "thoughts": state.get("thoughts", []) + ["Safety: Đã thêm cảnh báo rủi ro."],
        "citations": [],
    }


def create_advisor_graph() -> Any:
    """Create and compile the AI Advisor LangGraph workflow.

    Flow: router -> (conditional) -> analyst -> risk_manager -> (conditional) -> respond/safety_respond -> END
    """
    workflow = StateGraph(AdvisorState)

    workflow.add_node("router", router_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("risk_manager", risk_manager_node)
    workflow.add_node("respond", respond_node)
    workflow.add_node("safety_respond", safety_respond_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_intent,
        {"analyst": "analyst", "respond": "respond"},
    )

    workflow.add_edge("analyst", "risk_manager")

    workflow.add_conditional_edges(
        "risk_manager",
        lambda state: "respond" if state.get("is_safe", True) else "safety_respond",
        {"respond": "respond", "safety_respond": "safety_respond"},
    )

    workflow.add_edge("respond", END)
    workflow.add_edge("safety_respond", END)

    return workflow.compile()
