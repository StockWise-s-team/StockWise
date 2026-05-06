from typing import Any
from app.tools.base_tool import BaseTool


class WikiReaderTool(BaseTool):
    @property
    def name(self) -> str:
        return "wiki_reader"

    @property
    def description(self) -> str:
        return "Read aggregated company wiki information from the database."

    async def execute(self, input: str) -> Any:
        return {
            "symbol": input,
            "wiki_data": {
                "summary": "Apple Inc. designs and manufactures consumer electronics.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": "2.8T",
                "latest_news_synthesis": "Strong iPhone sales drive revenue growth.",
            },
        }
