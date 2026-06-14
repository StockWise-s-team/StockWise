from typing import Any

from langchain_core.runnables import RunnableConfig

from app.agents.master_router import MasterRouterAgent
from app.graph.state import AdvisorState


def _runtime(config: RunnableConfig) -> Any:
    return config["configurable"]["runtime"]


async def router_node(state: AdvisorState) -> dict[str, Any]:
    result = await MasterRouterAgent().run(state)
    if result.get("intent") in {"GREETING", "OUT_OF_SCOPE"}:
        result["symbols"] = []
    return result


async def route_intent(state: AdvisorState) -> str:
    return "respond" if state.get("intent") in {"GREETING", "OUT_OF_SCOPE"} else "context_planner"


async def context_planner_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    mapping = {
        "STOCK_OVERVIEW": ["market_data", "wiki_reader", "news_search"],
        "PRICE_EXPLANATION": ["market_data", "news_search"],
        "CHARTING": ["charting"],
        "CALCULATION": ["calculator"],
        "PORTFOLIO_RISK": ["portfolio_reader"],
        "TRACKED_SYMBOLS": ["tracked_symbols_reader"],
    }
    requested_symbols = state.get("symbols", [])
    symbols = await _runtime(config).validate_symbols(requested_symbols)
    return {
        "planned_tools": mapping.get(state.get("intent", ""), []),
        "requested_symbols": requested_symbols,
        "symbols": symbols,
        "thoughts": ["Planner: da chon cong cu."],
    }


async def _tool_node(tool_name: str, state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    if tool_name not in state.get("planned_tools", []):
        return {"thoughts": [f"{tool_name}: skipped"]}
    results = await _runtime(config).execute_tool(tool_name, state)
    if not isinstance(results, list):
        results = [results]
    return {"tool_results": [_serialize_tool_result(result) for result in results]}


def _serialize_tool_result(result: Any) -> dict[str, Any]:
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    return dict(result)


async def market_context_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    return await _tool_node("market_data", state, config)


async def wiki_context_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    return await _tool_node("wiki_reader", state, config)


async def news_context_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    return await _tool_node("news_search", state, config)


async def portfolio_context_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    return await _tool_node("portfolio_reader", state, config)


async def tracked_symbols_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    return await _tool_node("tracked_symbols_reader", state, config)


async def calculation_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    return await _tool_node("calculator", state, config)


async def chart_data_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    return await _tool_node("charting", state, config)


async def analyst_node(state: AdvisorState, config: RunnableConfig) -> dict[str, Any]:
    answer = await _runtime(config).generate_answer(state)
    return {"final_answer": answer, "thoughts": ["Analyst: da tong hop thong tin."]}


async def risk_manager_node(state: AdvisorState, config: RunnableConfig | None = None) -> dict[str, Any]:
    if config and config.get("configurable", {}).get("runtime"):
        return _runtime(config).sanitize_answer(state)
    return {"risk_flags": [], "is_safe": True, "thoughts": ["Risk Manager: da kiem tra an toan."]}


async def respond_node(state: AdvisorState) -> dict[str, Any]:
    answer = state.get("final_answer")
    if not answer and state.get("intent") == "GREETING":
        answer = "Xin chào. Tôi có thể hỗ trợ tra cứu dữ liệu cổ phiếu Việt Nam, danh mục, biểu đồ và phép tính lãi lỗ."
    if not answer:
        answer = "Tôi chỉ hỗ trợ các câu hỏi liên quan đến thị trường chứng khoán Việt Nam và danh mục đầu tư."
    return {"final_answer": answer, "thoughts": ["Respond: da chuan bi cau tra loi."]}


async def safety_respond_node(state: AdvisorState) -> dict[str, Any]:
    flags = sorted(set([*state.get("risk_flags", []), "SAFETY_BLOCKED"]))
    return {
        "final_answer": (
            "Xin lỗi, tôi không thể cung cấp câu trả lời này vì nội dung có dấu hiệu "
            "cam kết lợi nhuận hoặc khuyến nghị giao dịch trực tiếp. Vui lòng xem đây "
            "là thông tin tham khảo và tham vấn chuyên gia tài chính được cấp phép."
        ),
        "risk_flags": flags,
        "has_disclaimer": True,
        "thoughts": ["Safety: da chan cau tra loi khong an toan."],
    }
