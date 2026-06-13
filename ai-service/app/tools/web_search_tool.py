from typing import Any
from app.models.schemas import ToolResult
from app.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for the latest financial news and market data."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        """Disabled for security reasons."""
        return ToolResult(
            tool_name=self.name,
            success=False,
            error_code="TOOL_DISABLED",
            error_message="Web search tool is currently disabled.",
        )
