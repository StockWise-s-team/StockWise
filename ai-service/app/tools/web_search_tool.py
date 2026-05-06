from typing import Any
from app.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for the latest financial news and market data."

    async def execute(self, input: str) -> Any:
        return {
            "query": input,
            "results": [
                {"title": "Stock Market Today: Bullish Momentum Continues", "url": "https://example.com/news/1", "snippet": "Markets rallied on strong earnings..."},
                {"title": "Tech Sector Leads Gains", "url": "https://example.com/news/2", "snippet": "Technology stocks outperformed..."},
            ],
        }
