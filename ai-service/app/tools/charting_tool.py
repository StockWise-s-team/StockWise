from typing import Any
from app.models.schemas import ToolResult
from app.services.data_providers import MarketDataProvider
from app.tools.base_tool import BaseTool


class ChartingTool(BaseTool):
    def __init__(self, repository: MarketDataProvider):
        self.repository = repository

    @property
    def name(self) -> str:
        return "charting"

    @property
    def description(self) -> str:
        return "Generate chart data for candlestick, line, and technical indicator visualizations."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        """Query OHLCV market data from the repository for charting."""
        symbol = str(tool_input.get("symbol", "")).upper()
        try:
            ohlcv = await self.repository.get_ohlcv(symbol, limit=30)
        except Exception as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="PROVIDER_UNAVAILABLE",
                error_message=f"Lỗi truy vấn dữ liệu OHLCV cho {symbol}: {exc}",
            )
        if not ohlcv:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="DATA_UNAVAILABLE",
                error_message=f"Không có dữ liệu biểu đồ cho {symbol}.",
            )
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"symbol": symbol, "series": ohlcv},
        )
