from typing import Any

from app.config import settings
from app.models.schemas import Citation, ToolResult
from app.services.news_retriever import NewsRetriever
from app.tools.base_tool import BaseTool


class NewsSearchTool(BaseTool):
    def __init__(self, retriever: NewsRetriever):
        self.retriever = retriever

    @property
    def name(self) -> str:
        return "news_search"

    @property
    def description(self) -> str:
        return "Read recent persisted news articles by stock symbol."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        symbol = str(tool_input.get("symbol", "")).upper()
        articles = await self.retriever.search(symbol, limit=settings.AI_MAX_NEWS_RESULTS)
        if not articles:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_code="DATA_UNAVAILABLE",
                error_message=f"Chưa có tin tức gần đây cho {symbol}.",
            )
        source_type = "demo_fixture" if settings.AI_DATA_MODE == "demo" else "news_article"
        citations = [
            Citation(
                source_type=source_type,
                title=article["title"],
                reference=f"news_articles:{article['id']}",
                published_at=article.get("published_at"),
                url=article.get("url"),
            )
            for article in articles
        ]
        newest = articles[0].get("published_at") or articles[0].get("crawled_at")
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"articles": articles},
            citations=citations,
            freshness={"news_updated_at": str(newest) if newest else None},
        )
