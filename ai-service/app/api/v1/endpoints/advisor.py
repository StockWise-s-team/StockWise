import asyncio
import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.repositories.content_repo import ContentRepository
from app.db.repositories.market_repo import MarketRepository
from app.graph.advisor_graph import create_advisor_graph
from app.graph.graph_config import get_graph_config
from app.graph.state import AdvisorState
from app.models.schemas import ChatRequest, SourceRequest
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


def _build_initial_state(
    request: ChatRequest,
    user_id: str,
) -> AdvisorState:
    """Build the initial AdvisorState from the chat request.

    Args:
        request: ChatRequest with message and optional session_id.
        user_id: Authenticated user ID from header.

    Returns:
        Initial AdvisorState for LangGraph workflow.
    """
    session_id = request.session_id or str(uuid.uuid4())
    return {
        "user_message": request.message,
        "user_id": user_id,
        "session_id": session_id,
        "conversation_history": [],
        "intent": "",
        "symbols": [],
        "requires_portfolio": False,
        "tool_results": [],
        "portfolio_context": None,
        "thoughts": [],
        "streaming_tokens": [],
        "risk_flags": [],
        "is_safe": True,
        "final_answer": "",
        "citations": [],
        "error": None,
    }


async def _run_graph(
    state: AdvisorState,
    sse_manager: SSEManager,
    db: AsyncSession,
) -> None:
    """Execute the LangGraph workflow and emit SSE events.

    Args:
        state: Initial AdvisorState.
        sse_manager: SSEManager for event emission.
        db: Database session.
    """
    try:
        graph = create_advisor_graph()
        config = get_graph_config(state["session_id"])

        await sse_manager.emit_thought("Đang phân tích yêu cầu của bạn...", node="router")

        result = await graph.ainvoke(state, config=config)

        if result.get("final_answer"):
            await sse_manager.emit_final(
                answer=result["final_answer"],
                citations=result.get("citations", []),
                intent=result.get("intent", ""),
                symbols=result.get("symbols", []),
                has_disclaimer=not result.get("is_safe", True),
            )
        else:
            await sse_manager.emit_error(
                "Không thể tạo câu trả lời.",
                "GRAPH_NO_ANSWER",
            )

    except Exception as e:
        await sse_manager.emit_error(str(e), "GRAPH_ERROR")
    finally:
        await sse_manager.close()


@router.post("/advisor/chat")
async def advisor_chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI Advisor chat endpoint with SSE streaming.

    Args:
        request: ChatRequest with message and optional session_id.
        user_id: Authenticated user ID from X-User-Id header.
        db: Database session.

    Returns:
        EventSourceResponse with SSE stream of thought, token, and final events.
    """
    state = _build_initial_state(request, user_id)
    sse_manager = SSEManager()

    async def run_graph_task() -> None:
        await _run_graph(state, sse_manager, db)

    asyncio.create_task(run_graph_task())

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
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI Advisor chat endpoint for EventSource (GET with query param).

    Args:
        message: User message.
        user_id: Authenticated user ID from X-User-Id header.
        db: Database session.

    Returns:
        EventSourceResponse with SSE stream.
    """
    request = ChatRequest(message=message)
    state = _build_initial_state(request, user_id)
    sse_manager = SSEManager()

    async def run_graph_task() -> None:
        await _run_graph(state, sse_manager, db)

    asyncio.create_task(run_graph_task())

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
