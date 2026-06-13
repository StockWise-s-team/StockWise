from typing import Any
from app.models.schemas import ToolResult
from app.tools.base_tool import BaseTool


class TextToSQLTool(BaseTool):
    @property
    def name(self) -> str:
        return "text_to_sql"

    @property
    def description(self) -> str:
        return "Convert natural language queries into SQL for the market database."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        """Disabled for security reasons."""
        return ToolResult(
            tool_name=self.name,
            success=False,
            error_code="TOOL_DISABLED",
            error_message="Text-to-SQL tool is currently disabled.",
        )
