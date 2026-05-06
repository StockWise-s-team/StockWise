from typing import Any
from app.tools.base_tool import BaseTool


class ChartingTool(BaseTool):
    @property
    def name(self) -> str:
        return "charting"

    @property
    def description(self) -> str:
        return "Generate chart data for candlestick, line, and technical indicator visualizations."

    async def execute(self, input: str) -> Any:
        return {
            "symbol": input,
            "chart_type": "candlestick",
            "data": {
                "labels": ["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04", "2026-05-05"],
                "datasets": [
                    {"label": "Close", "data": [170.50, 172.30, 174.10, 173.80, 175.20]},
                    {"label": "SMA50", "data": [171.00, 171.50, 172.00, 172.50, 173.00]},
                ],
            },
        }
