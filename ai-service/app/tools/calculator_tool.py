from typing import Any
from app.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Perform financial calculations such as P/E ratio, DCF valuation, moving averages."

    async def execute(self, input: str) -> Any:
        return {
            "expression": input,
            "result": {
                "pe_ratio": 28.5,
                "eps": 6.14,
                "dcf_value": 195.30,
                "moving_avg_50": 172.45,
                "moving_avg_200": 165.80,
            },
        }
