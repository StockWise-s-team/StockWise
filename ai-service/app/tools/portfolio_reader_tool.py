from typing import Any

from app.config import settings
from app.models.schemas import Citation, ToolResult
from app.services.data_providers import PortfolioProvider
from app.tools.base_tool import BaseTool


class PortfolioReaderTool(BaseTool):
    def __init__(self, repository: PortfolioProvider):
        self.repository = repository

    @property
    def name(self) -> str:
        return "portfolio_reader"

    @property
    def description(self) -> str:
        return "Read a user's portfolio, holdings, value, and unrealized PnL."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        try:
            portfolio = await self.repository.get_portfolio(str(tool_input.get("user_id", "")))
        except Exception:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="PROVIDER_UNAVAILABLE",
                error_message="Nguồn dữ liệu danh mục hiện không khả dụng.",
            )
        if not portfolio:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="DATA_UNAVAILABLE",
                error_message="Khong tim thay danh muc cua nguoi dung.",
            )
        source_type = "demo_fixture" if settings.AI_DATA_MODE == "demo" else "market_db"
        return ToolResult(
            tool_name=self.name,
            success=True,
            data=portfolio,
            citations=[Citation(source_type=source_type, title="Danh muc dau tu", reference="portfolios:current-user")],
            freshness={},
        )
