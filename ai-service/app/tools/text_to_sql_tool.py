from typing import Any
from app.tools.base_tool import BaseTool


class TextToSQLTool(BaseTool):
    @property
    def name(self) -> str:
        return "text_to_sql"

    @property
    def description(self) -> str:
        return "Convert natural language queries into SQL for the market database."

    async def execute(self, input: str) -> Any:
        return {
            "query": input,
            "sql": "SELECT date, open, high, low, close, volume FROM market_data WHERE symbol = 'AAPL' ORDER BY date DESC LIMIT 30",
            "results": "mock_sql_results",
        }
