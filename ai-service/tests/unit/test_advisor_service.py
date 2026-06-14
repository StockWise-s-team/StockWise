import pytest

from app.models.schemas import ToolResult
from app.services.advisor_service import AdvisorService
from app.streaming.sse_manager import SSEManager


class FakeMarketProvider:
    def __init__(self, fail=False):
        self.fail = fail

    async def get_latest_price(self, symbol):
        if self.fail:
            raise RuntimeError("database down")
        return {"symbol": symbol} if symbol == "FPT" else None


class FakeTool:
    def __init__(self):
        self.inputs = []

    async def execute(self, tool_input):
        self.inputs.append(tool_input)
        return ToolResult(tool_name="market_data", success=True, data={"symbol": tool_input["symbol"]})


class FakeRegistry:
    def __init__(self, tool):
        self.tool = tool

    def get(self, name):
        return self.tool


def test_stale_market_data_adds_risk_flag():
    service = object.__new__(AdvisorService)
    assert "STALE_DATA" in service._add_stale_flag([], {"market_updated_at": "2000-01-01"})


def test_stale_market_data_ignores_invalid_date():
    service = object.__new__(AdvisorService)
    assert service._add_stale_flag(["EXISTING"], {"market_updated_at": "not-a-date"}) == ["EXISTING"]


@pytest.mark.asyncio
async def test_validate_symbols_fails_closed_on_provider_error():
    service = object.__new__(AdvisorService)
    service.market_provider = FakeMarketProvider(fail=True)
    assert await service.validate_symbols(["FPT"]) == []


@pytest.mark.asyncio
async def test_execute_symbol_tool_runs_once_per_symbol():
    service = object.__new__(AdvisorService)
    tool = FakeTool()
    service.registry = FakeRegistry(tool)
    service.sink = SSEManager("session-1")

    results = await service.execute_tool("market_data", {"symbols": ["FPT", "VIC"]})

    assert [item.data["symbol"] for item in results] == ["FPT", "VIC"]
    assert tool.inputs == [{"symbol": "FPT"}, {"symbol": "VIC"}]


def test_calculation_input_uses_semantic_pnl_order():
    service = object.__new__(AdvisorService)
    assert service._calculation_input("mua 25.5 ban 30 voi 100 co") == {
        "operation": "pnl",
        "quantity": 100,
        "buy_price": 25.5,
        "sell_price": 30,
    }
