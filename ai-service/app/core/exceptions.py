class StockWiseAIException(Exception):
    """Base exception for AI service."""


class LLMUnavailableError(StockWiseAIException):
    """Primary LLM (Gemini) is unavailable."""


class ToolExecutionError(StockWiseAIException):
    """Tool failed to return results."""

    def __init__(self, tool_name: str, reason: str) -> None:
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' failed: {reason}")


class SymbolNotFoundError(StockWiseAIException):
    """Stock symbol not in database."""


class DataUnavailableError(StockWiseAIException):
    """Data exists but is stale or incomplete."""


class SafetyViolationError(StockWiseAIException):
    """Response violates safety rules."""
