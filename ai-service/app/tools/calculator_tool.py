from typing import Any
from app.models.schemas import ToolResult
from app.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Perform basic financial calculations like profit & loss (PnL) and position sizing."

    async def execute(self, tool_input: dict[str, Any]) -> ToolResult:
        """Perform PnL or position calculations based on input variables."""
        operation = tool_input.get("operation")
        if operation == "pnl":
            try:
                qty = float(tool_input["quantity"])
                buy = float(tool_input["buy_price"])
                sell = float(tool_input["sell_price"])
                pnl = (sell - buy) * qty
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={"result": pnl},
                )
            except KeyError:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error_code="INVALID_CALCULATION",
                    error_message="Calculator requires quantity, buy_price, and sell_price for pnl calculation.",
                )
        return ToolResult(
            tool_name=self.name,
            success=False,
            error_code="INVALID_CALCULATION",
            error_message=f"Unsupported calculator operation: {operation}",
        )
