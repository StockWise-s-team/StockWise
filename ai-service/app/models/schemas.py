from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID


class ChatRequest(BaseModel):
    """Request body for the AI Advisor chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000,
                         description="User message in Vietnamese or English")
    session_id: Optional[str] = Field(
        None,
        description="UUID for conversation session. If omitted, a new session is created.",
    )

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
