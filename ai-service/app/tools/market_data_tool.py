from typing import Any

from app.config import settings
from app.models.schemas import Citation, ToolResult
from app.services.data_providers import MarketDataProvider
from app.tools.base_tool import BaseTool


class MarketDataTool(BaseTool):
    def __init__(self, repository: MarketDataProvider):
        self.repository = repository

    @property
    def name(self) -> str:
        return "market_data"

    @property
    def description(self) -> str:
        return "Read bounded OHLCV and financial ratio data for a validated symbol."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        symbol = str(tool_input.get("symbol", "")).upper()
        try:
            latest = await self.repository.get_latest_price(symbol)
            ratios = await self.repository.get_financial_ratios(symbol) if latest else []
        except Exception:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="PROVIDER_UNAVAILABLE",
                error_message="Nguồn dữ liệu thị trường hiện không khả dụng.",
            )
        if not latest:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="DATA_UNAVAILABLE",
                error_message=f"Không có dữ liệu thị trường cho {symbol or 'mã cổ phiếu này'}.",
            )
        freshness = str(latest["trade_date"]) if latest.get("trade_date") else None
        source_type = "demo_fixture" if settings.AI_DATA_MODE == "demo" else "market_db"
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"latest_price": latest, "financial_ratios": ratios},
            citations=[Citation(source_type=source_type, title=f"Du lieu thi truong {symbol}", reference=f"stock_prices:{symbol}")],
            freshness={"market_updated_at": freshness},
        )
