from typing import Annotated, Any, Optional
import operator
from typing import TypedDict


class ToolResult(TypedDict):
    """Result from a tool execution."""
    tool_name: str
    tool_input: dict
    tool_output: Any
    success: bool
    error: Optional[str]


class PortfolioContext(TypedDict):
    """User portfolio context for portfolio-aware responses."""
    user_id: str
    holdings: list[dict]
    total_value: float
    unrealized_pnl: float
    fetched_at: str


class AdvisorState(TypedDict):
    """State for the AI Advisor LangGraph workflow.

    Fields are designed to be updated by graph nodes sequentially.
    Lists use Annotated[..., operator.add] to accumulate across nodes.
    """
    # Input
    user_message: str
    user_id: str
    session_id: str
    conversation_history: list[dict]

    # Routing
    intent: str
    symbols: list[str]
    requires_portfolio: bool

    # Retrieved Data
    tool_results: Annotated[list[ToolResult], operator.add]
    portfolio_context: Optional[PortfolioContext]

    # Streaming
    thoughts: Annotated[list[str], operator.add]
    streaming_tokens: Annotated[list[str], operator.add]

    # Risk
    risk_flags: list[str]
    is_safe: bool

    # Output
    final_answer: str
    citations: list[str]
    error: Optional[str]
