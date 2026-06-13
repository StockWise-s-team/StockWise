from typing import Any
from app.db.repositories.content_repo import ContentRepository
from app.models.schemas import ToolResult, Citation
from app.tools.base_tool import BaseTool


class WikiReaderTool(BaseTool):
    def __init__(self, repository: ContentRepository):
        self.repository = repository

    @property
    def name(self) -> str:
        return "wiki_reader"

    @property
    def description(self) -> str:
        return "Read aggregated company wiki information from the database."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        """Query PostgreSQL to get the latest synthesized wiki profile for the symbol."""
        symbol = str(tool_input.get("symbol", "")).upper()
        try:
            wiki = await self.repository.get_wiki(symbol)
        except Exception as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="DATABASE_ERROR",
                error_message=f"Lỗi truy vấn cơ sở dữ liệu wiki cho {symbol}: {exc}",
            )

        if not wiki:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="DATA_UNAVAILABLE",
                error_message=f"Chưa có thông tin wiki cho cổ phiếu {symbol}.",
            )

        wiki_data = wiki.get("wiki_data") or {}
        version = wiki.get("version", 1)
        updated_at = wiki.get("updated_at")

        citations = [
            Citation(
                source_type="company_wiki",
                title=f"Bản tổng hợp doanh nghiệp {symbol} v{version}",
                reference=f"company_wiki:{symbol}",
            )
        ]

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"symbol": symbol, "wiki_data": wiki_data, "version": version},
            citations=citations,
            freshness={"wiki_updated_at": str(updated_at) if updated_at else None},
        )
