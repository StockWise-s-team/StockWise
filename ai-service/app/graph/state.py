from typing import Annotated, Any, Optional, TypedDict
import operator


ToolResultState = dict[str, Any]


class AdvisorState(TypedDict):
    user_message: str
    user_id: str
    session_id: str
    conversation_history: list[dict[str, str]]
    intent: str
    symbols: list[str]
    requested_symbols: list[str]
    requires_portfolio: bool
    planned_tools: list[str]
    tool_results: Annotated[list[ToolResultState], operator.add]
    portfolio_context: Optional[dict[str, Any]]
    thoughts: Annotated[list[str], operator.add]
    streaming_tokens: Annotated[list[str], operator.add]
    risk_flags: list[str]
    is_safe: bool
    has_disclaimer: bool
    final_answer: str
    citations: list[dict[str, Any]]
    data_mode: str
    data_freshness: dict[str, str | None]
    error: Optional[str]
