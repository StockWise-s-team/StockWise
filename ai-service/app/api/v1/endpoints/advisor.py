import asyncio
import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.repositories.chat_repo import ChatRepository
from app.db.repositories.content_repo import ContentRepository
from app.models.schemas import ChatMessageView, ChatRequest, ChatSessionSummary, SourceRequest
from app.services.advisor_service import AdvisorService
from app.streaming.sse_manager import SSEManager

router = APIRouter()


def _require_admin(role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    """Require admin role for admin endpoints."""
    resolved = role or x_role
    if resolved != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")


def _json_default(value: Any) -> str | float:
    """JSON serializer for datetime and Decimal types."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


@router.get("/advisor/sessions", response_model=list[ChatSessionSummary])
async def list_advisor_sessions(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List persisted advisor sessions owned by the current user."""
    sessions = await ChatRepository(db).list_sessions(user_id)
    return [
        ChatSessionSummary(
            id=str(session.id),
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        for session in sessions
    ]


@router.get("/advisor/sessions/{session_id}/messages", response_model=list[ChatMessageView])
async def list_advisor_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List persisted advisor messages after verifying session ownership."""
    try:
        messages = await ChatRepository(db).list_messages_for_user(session_id, user_id)
    except (PermissionError, ValueError):
        raise HTTPException(status_code=404, detail="Chat session not found") from None
    return [
        ChatMessageView(
            id=str(message.id),
            session_id=str(message.session_id),
            role=message.role,
            content=message.content,
            metadata=message.message_metadata or {},
            created_at=message.created_at,
        )
        for message in messages
    ]


@router.delete("/advisor/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_advisor_session(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an advisor session owned by the current user."""
    try:
        deleted = await ChatRepository(db).delete_session(session_id, user_id)
    except ValueError:
        deleted = False
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/advisor/chat")
async def advisor_chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI Advisor chat endpoint with SSE streaming.

    Constructs AdvisorService to process the message via LangGraph and streams tokens back.
    """
    session_id = request.session_id or str(uuid.uuid4())
    # Ensure requests from endpoint carry the validated session_id
    request.session_id = session_id
    sse_manager = SSEManager(session_id=session_id)

    async def run_advisor_task() -> None:
        try:
            service = AdvisorService(db, sse_manager)
            await service.process(request, user_id)
        except Exception as e:
            await sse_manager.emit_error(str(e), "INTERNAL_ERROR")
        finally:
            await sse_manager.emit("done", {"status": "complete"})
            await asyncio.sleep(0.05)
            await sse_manager.close()

    asyncio.create_task(run_advisor_task())

    async def event_generator():
        while True:
            event = await sse_manager.queue.get()
            if event is None:
                break
            yield ServerSentEvent(data=event.data, event=event.event)

    return EventSourceResponse(event_generator())


@router.get("/advisor/chat/stream")
async def advisor_chat_stream(
    message: str = Query(..., min_length=1),
    session_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI Advisor chat endpoint for EventSource (GET with query param)."""
    request = ChatRequest(message=message, session_id=session_id)
    resolved_session_id = request.session_id or str(uuid.uuid4())
    request.session_id = resolved_session_id
    sse_manager = SSEManager(session_id=resolved_session_id)

    async def run_advisor_task() -> None:
        try:
            service = AdvisorService(db, sse_manager)
            await service.process(request, user_id)
        except Exception as e:
            await sse_manager.emit_error(str(e), "INTERNAL_ERROR")
        finally:
            await sse_manager.emit("done", {"status": "complete"})
            await asyncio.sleep(0.05)
            await sse_manager.close()

    asyncio.create_task(run_advisor_task())

    async def event_generator():
        while True:
            event = await sse_manager.queue.get()
            if event is None:
                break
            yield ServerSentEvent(data=event.data, event=event.event)

    return EventSourceResponse(event_generator())


@router.get("/admin/sources")
async def list_sources(
    role: str = Header(None),
    x_role: str = Header(None, alias="X-Role"),
    db: AsyncSession = Depends(get_db),
):
    """List all news sources. Admin only."""
    _require_admin(role=role, x_role=x_role)
    return {"sources": await ContentRepository(db).list_sources()}


@router.post("/admin/sources")
async def add_source(
    source: SourceRequest,
    role: str = Header(None),
    x_role: str = Header(None, alias="X-Role"),
    db: AsyncSession = Depends(get_db),
):
    """Add a new news source. Admin only."""
    _require_admin(role=role, x_role=x_role)
    new_source = await ContentRepository(db).add_source(source.name, source.base_url, source.crawler_type)
    return {"source": new_source}


@router.patch("/admin/sources/{source_id}")
async def toggle_source(
    source_id: str,
    role: str = Header(None),
    x_role: str = Header(None, alias="X-Role"),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a news source active state. Admin only."""
    _require_admin(role=role, x_role=x_role)
    source = await ContentRepository(db).toggle_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"source": source}


@router.delete("/admin/sources/{source_id}")
async def delete_source(
    source_id: str,
    role: str = Header(None),
    x_role: str = Header(None, alias="X-Role"),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a news source. Admin only."""
    _require_admin(role=role, x_role=x_role)
    source = await ContentRepository(db).deactivate_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"source": source}


@router.get("/admin/wiki/{symbol}")
async def get_wiki_state(symbol: str, db: AsyncSession = Depends(get_db)):
    """Get company wiki state by symbol."""
    wiki = await ContentRepository(db).get_wiki(symbol)
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found for symbol")
    return {"wiki": wiki}


@router.get("/admin/wiki/{symbol}/history")
async def get_wiki_history(symbol: str, db: AsyncSession = Depends(get_db)):
    """Get company wiki version history by symbol."""
    history = await ContentRepository(db).get_wiki_history(symbol)
    return {"symbol": symbol.upper(), "history": history}


@router.post("/admin/wiki/{symbol}/trigger")
async def trigger_synthesis(
    symbol: str,
    role: str = Header(None),
    x_role: str = Header(None, alias="X-Role"),
):
    """Trigger wiki synthesis for a symbol. Admin only."""
    _require_admin(role=role, x_role=x_role)
    return {
        "status": "accepted",
        "symbol": symbol.upper(),
        "message": "Synthesis trigger accepted by API. Queue-backed execution should be wired by the data-pipeline owner.",
    }
