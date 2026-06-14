from typing import Any

from app.models.schemas import Citation, ToolResult
from app.tools.base_tool import BaseTool


class TrackedSymbolsTool(BaseTool):
    def __init__(self, repository):
        self.repository = repository

    @property
    def name(self) -> str:
        return "tracked_symbols_reader"

    @property
    def description(self) -> str:
        return "Read the stock symbols currently tracked by the AI/data pipeline and selected by the user."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        user_id = str(tool_input.get("user_id", ""))
        data = await self.repository.get_tracked_symbols(user_id)
        symbols = data.get("tracked_symbols", [])

        if not symbols:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="NO_TRACKED_SYMBOLS",
                error_message="Chua co ma co phieu nao trong danh sach theo doi.",
            )

        return ToolResult(
            tool_name=self.name,
            success=True,
            data=data,
            citations=[
                Citation(
                    source_type="database",
                    title="Danh sach ma co phieu dang theo doi",
                    reference="tracked_symbols:user-and-system",
                )
            ],
        )
