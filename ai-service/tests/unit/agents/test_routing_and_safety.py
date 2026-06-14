import asyncio

from app.agents.master_router import deterministic_route
from app.agents.risk_manager_agent import RiskManagerAgent
from app.graph.nodes import router_node, safety_respond_node


def test_deterministic_router_handles_chart():
    decision = deterministic_route("Ve bieu do FPT")
    assert decision.intent == "CHARTING"
    assert decision.symbols == ["FPT"]


def test_deterministic_router_handles_tracked_symbols_question():
    decision = deterministic_route("AI hien dang track nhung co phieu nao?")
    assert decision.intent == "TRACKED_SYMBOLS"
    assert decision.symbols == []


def test_greeting_symbols_are_removed_by_graph_router():
    result = asyncio.run(router_node({"user_message": "Xin chao"}))
    assert result["intent"] == "GREETING"
    assert result["symbols"] == []


def test_safety_adds_disclaimer_for_trading_related_answer():
    answer, flags, has_disclaimer = RiskManagerAgent().sanitize("Du lieu FPT.", "Phan tich FPT", "STOCK_OVERVIEW")
    assert has_disclaimer is True
    assert "MISSING_DISCLAIMER" in flags
    assert "khuyến nghị" in answer


def test_safety_flags_guaranteed_return_and_all_in():
    _, flags, _ = RiskManagerAgent().sanitize("", "Dam bao VIC tang va all-in", "STOCK_OVERVIEW")
    assert "GUARANTEED_RETURN" in flags
    assert "DIRECT_BUY_SELL_COMMAND" in flags


def test_safety_marks_unrealistic_guarantee_unsafe():
    review = RiskManagerAgent().review("FPT cam ket lai 50%.", "Phan tich FPT", "STOCK_OVERVIEW", [])
    assert review.is_safe is False
    assert "UNREALISTIC_GUARANTEE" in review.risk_flags


def test_safety_blocks_unsafe_answer():
    result = asyncio.run(
        safety_respond_node(
            {
                "final_answer": "FPT cam ket lai 50%.",
                "risk_flags": ["UNREALISTIC_GUARANTEE"],
            }
        )
    )
    assert "cam ket lai 50%" not in result["final_answer"]
    assert "SAFETY_BLOCKED" in result["risk_flags"]


def test_deterministic_router_covers_supported_intents():
    cases = {
        "Xin chao": "GREETING",
        "Phan tich FPT": "STOCK_OVERVIEW",
        "Tai sao FPT tang": "PRICE_EXPLANATION",
        "Tinh lai lo 100 10 12": "CALCULATION",
        "Ve bieu do FPT": "CHARTING",
        "Danh muc cua toi": "PORTFOLIO_RISK",
        "Hom nay thoi tiet the nao": "OUT_OF_SCOPE",
    }
    assert {message: deterministic_route(message).intent for message in cases} == cases


def test_deterministic_router_avoids_fuzzy_false_positives():
    assert deterministic_route("Tinh cach nha dau tu la gi?").intent == "OUT_OF_SCOPE"
    assert deterministic_route("Toi muon xem ve doanh nghiep noi chung").intent == "OUT_OF_SCOPE"


def test_deterministic_router_uses_symbol_aliases():
    decision = deterministic_route("Phan tich Techcombank")
    assert decision.intent == "STOCK_OVERVIEW"
    assert decision.symbols == ["TCB"]
