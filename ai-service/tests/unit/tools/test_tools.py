from datetime import date

import pytest

from app.tools.calculator_tool import CalculatorTool
from app.tools.charting_tool import ChartingTool
from app.tools.market_data_tool import MarketDataTool
from app.tools.news_search_tool import NewsSearchTool
from app.tools.portfolio_reader_tool import PortfolioReaderTool
from app.tools.tracked_symbols_tool import TrackedSymbolsTool
from app.tools.text_to_sql_tool import TextToSQLTool
from app.tools.web_search_tool import WebSearchTool
from app.tools.wiki_reader_tool import WikiReaderTool


class FakeMarketRepository:
    async def get_latest_price(self, symbol):
        if symbol == "MISSING":
            return None
        return {"symbol": symbol, "trade_date": date(2026, 5, 30), "close": 100, "volume": 50}

    async def get_financial_ratios(self, symbol):
        return []

    async def get_ohlcv(self, symbol, limit):
        if symbol == "MISSING":
            return []
        return [{"symbol": symbol, "trade_date": date(2026, 5, 30), "close": 100}]


class FakeContentRepository:
    async def get_wiki(self, symbol):
        if symbol == "MISSING":
            return None
        return {"symbol": symbol, "wiki_data": {"summary": "verified"}, "updated_at": None}


class FakeNewsRetriever:
    async def search(self, symbol, limit):
        return [] if symbol == "MISSING" else [{"id": "1", "title": "verified", "url": None, "published_at": None, "crawled_at": None}]


class FakePortfolioRepository:
    async def get_portfolio(self, user_id):
        return None if user_id == "missing" else {"holdings": [], "total_value": 0, "unrealized_pnl": 0}


class FakeTrackedSymbolsRepository:
    async def get_tracked_symbols(self, user_id):
        if user_id == "empty":
            return {
                "tracked_symbols": [],
                "user_tracked_symbols": [],
                "system_tracked_symbols": [],
                "selection_scope": "system",
            }
        return {
            "tracked_symbols": ["FPT", "HPG", "VNM"],
            "user_tracked_symbols": ["FPT", "HPG", "VNM"],
            "system_tracked_symbols": ["FPT", "HPG", "VNM"],
            "selection_scope": "user",
        }


@pytest.mark.asyncio
async def test_market_tool_returns_traceable_data():
    result = await MarketDataTool(FakeMarketRepository()).execute({"symbol": "FPT"})
    assert result.success is True
    assert result.citations[0].reference == "stock_prices:FPT"


@pytest.mark.asyncio
async def test_market_tool_reports_missing_data():
    result = await MarketDataTool(FakeMarketRepository()).execute({"symbol": "MISSING"})
    assert result.success is False
    assert result.error_code == "DATA_UNAVAILABLE"
    assert result.citations == []


@pytest.mark.asyncio
async def test_wiki_tool_has_no_invented_url():
    result = await WikiReaderTool(FakeContentRepository()).execute({"symbol": "FPT"})
    assert result.success is True
    assert result.citations[0].url is None


@pytest.mark.asyncio
async def test_wiki_tool_reports_missing_data():
    result = await WikiReaderTool(FakeContentRepository()).execute({"symbol": "MISSING"})
    assert result.error_code == "DATA_UNAVAILABLE"


@pytest.mark.asyncio
async def test_news_tool_reports_missing_data_without_citations():
    result = await NewsSearchTool(FakeNewsRetriever()).execute({"symbol": "MISSING"})
    assert result.error_code == "DATA_UNAVAILABLE"
    assert result.citations == []


@pytest.mark.asyncio
async def test_portfolio_tool_reports_missing_data():
    result = await PortfolioReaderTool(FakePortfolioRepository()).execute({"user_id": "missing"})
    assert result.error_code == "DATA_UNAVAILABLE"


@pytest.mark.asyncio
async def test_tracked_symbols_tool_returns_user_selection():
    result = await TrackedSymbolsTool(FakeTrackedSymbolsRepository()).execute({"user_id": "user-1"})
    assert result.success is True
    assert result.data["tracked_symbols"] == ["FPT", "HPG", "VNM"]
    assert result.citations[0].reference == "tracked_symbols:user-and-system"


@pytest.mark.asyncio
async def test_calculator_is_deterministic():
    result = await CalculatorTool().execute({"operation": "pnl", "quantity": 100, "buy_price": 10, "sell_price": 12})
    assert result.data["result"] == 200


@pytest.mark.asyncio
async def test_calculator_supports_return_pct():
    result = await CalculatorTool().execute({"operation": "return_pct", "buy_price": 10, "sell_price": 12})
    assert result.data["result"] == 20


@pytest.mark.asyncio
async def test_calculator_supports_position_sizing():
    result = await CalculatorTool().execute({"operation": "position_sizing", "budget": 105, "price": 10})
    assert result.data["result"] == 10


@pytest.mark.asyncio
async def test_calculator_supports_fee_tax_for_sell_side():
    result = await CalculatorTool().execute({"operation": "fee_tax", "quantity": 100, "price": 10, "side": "sell"})
    assert result.data["trading_fee"] == 1.5
    assert result.data["sell_tax"] == 1


@pytest.mark.asyncio
async def test_calculator_rejects_missing_arguments():
    result = await CalculatorTool().execute({"operation": "pnl"})
    assert result.error_code == "INVALID_CALCULATION"


@pytest.mark.asyncio
async def test_chart_uses_repository_rows():
    result = await ChartingTool(FakeMarketRepository()).execute({"symbol": "FPT"})
    assert result.success is True
    assert result.data["series"][0]["close"] == 100


@pytest.mark.asyncio
async def test_chart_reports_missing_data():
    result = await ChartingTool(FakeMarketRepository()).execute({"symbol": "MISSING"})
    assert result.error_code == "DATA_UNAVAILABLE"


@pytest.mark.asyncio
async def test_legacy_untraceable_tools_are_disabled():
    assert (await TextToSQLTool().execute({"query": "anything"})).error_code == "TOOL_DISABLED"
    assert (await WebSearchTool().execute({"query": "anything"})).error_code == "TOOL_DISABLED"
