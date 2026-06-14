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
        if operation == "return_pct":
            try:
                buy = float(tool_input["buy_price"])
                sell = float(tool_input["sell_price"])
                if buy == 0:
                    raise ValueError("buy_price must be non-zero")
                return_pct = ((sell - buy) / buy) * 100
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={"result": return_pct, "unit": "percent"},
                )
            except (KeyError, ValueError):
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error_code="INVALID_CALCULATION",
                    error_message="Calculator requires non-zero buy_price and sell_price for return_pct calculation.",
                )
        if operation == "position_sizing":
            try:
                budget = float(tool_input["budget"])
                price = float(tool_input["price"])
                if price <= 0:
                    raise ValueError("price must be positive")
                quantity = int(budget // price)
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={"result": quantity, "unit": "shares"},
                )
            except (KeyError, ValueError):
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error_code="INVALID_CALCULATION",
                    error_message="Calculator requires budget and positive price for position_sizing calculation.",
                )
        if operation == "fee_tax":
            try:
                qty = float(tool_input["quantity"])
                price = float(tool_input["price"])
                side = str(tool_input.get("side", "buy")).lower()
                gross_value = qty * price
                trading_fee = gross_value * 0.0015
                sell_tax = gross_value * 0.001 if side == "sell" else 0
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={
                        "gross_value": gross_value,
                        "trading_fee": trading_fee,
                        "sell_tax": sell_tax,
                        "total_cost": trading_fee + sell_tax,
                    },
                )
            except (KeyError, ValueError):
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error_code="INVALID_CALCULATION",
                    error_message="Calculator requires quantity and price for fee_tax calculation.",
                )
        return ToolResult(
            tool_name=self.name,
            success=False,
            error_code="INVALID_CALCULATION",
            error_message=f"Unsupported calculator operation: {operation}",
        )
