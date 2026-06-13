from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Any, List, Optional
from uuid import UUID


class ChatRequest(BaseModel):
    """Request body for the AI Advisor chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000,
                         description="User message in Vietnamese or English")
    session_id: Optional[str] = Field(
        None,
        description="UUID for conversation session. If omitted, a new session is created.",
    )
    user_id: Optional[str] = None

    @field_validator("session_id")
    @classmethod
    def validate_uuid(cls, v: Optional[str]) -> Optional[str]:
        """Validate session_id is a valid UUID string."""
        if v is not None:
            UUID(v)
        return v


class ChatEvent(BaseModel):
    """SSE event for chat streaming."""
    type: str
    content: str


class SourceRequest(BaseModel):
    """Request body for adding a news source."""
    name: str
    base_url: str
    crawler_type: str


class WikiState(BaseModel):
    """Company wiki state."""
    symbol: str
    wiki_data: dict
    version: int


class Citation(BaseModel):
    """RAG Source citation."""
    source_type: str
    title: str
    reference: str
    published_at: Optional[Any] = None
    url: Optional[str] = None


class ToolResult(BaseModel):
    """Standard tool execution result."""
    tool_name: str
    success: bool
    data: Optional[Any] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    citations: List[Citation] = []
    freshness: dict = {}


class SSEEnvelope(BaseModel):
    """SSE envelope for event streaming."""
    type: str
    data: dict
    session_id: str
    sequence: int


class ChatSessionSummary(BaseModel):
    """Persisted advisor chat session summary."""
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ChatMessageView(BaseModel):
    """Persisted advisor chat message view."""
    id: str
    session_id: str
    role: str
    content: str
    metadata: dict[str, Any] = {}
    created_at: datetime


class FinalAnswer(BaseModel):
    """Final answer object structure."""
    answer: str
    citations: List[Citation] = []
    intent: str = ""
    symbols: List[str] = []
    risk_flags: List[str] = []
    has_disclaimer: bool = False
    data_mode: str = "live"
    data_freshness: dict = {}
