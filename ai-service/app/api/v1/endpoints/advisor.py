import asyncio
import json
from fastapi import APIRouter, Request, HTTPException, Query, Header
from sse_starlette.sse import EventSourceResponse
from app.models.schemas import ChatRequest, SourceRequest, WikiState

router = APIRouter()

MOCK_SOURCES = [
    {"id": "1", "name": "Reuters Finance", "base_url": "https://reuters.com/finance", "crawler_type": "rss", "active": True},
    {"id": "2", "name": "Bloomberg Markets", "base_url": "https://bloomberg.com/markets", "crawler_type": "api", "active": True},
]

MOCK_WIKI = {
    "AAPL": {
        "symbol": "AAPL",
        "wiki_data": {"summary": "Apple Inc. designs, manufactures and markets smartphones and personal computers.", "sector": "Technology", "ceo": "Tim Cook"},
        "version": 3,
        "history": [
            {"version": 1, "timestamp": "2026-05-01T10:00:00Z", "source": "Reuters Finance"},
            {"version": 2, "timestamp": "2026-05-02T14:00:00Z", "source": "Bloomberg Markets"},
            {"version": 3, "timestamp": "2026-05-04T09:00:00Z", "source": "Reuters Finance"},
        ],
    }
}


def _require_admin(role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    resolved = role or x_role
    if resolved != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")


async def _generate_thought_events():
    thoughts = [
        "Analyzing your query...",
        "Routing to technical analysis agent...",
        "Pulling market data for relevant symbols...",
        "Running risk assessment...",
    ]
    for thought in thoughts:
        yield {"event": "thought", "data": json.dumps({"type": "thought", "content": thought})}
        await asyncio.sleep(0.5)

    final_answer = (
        "Based on technical analysis, the current trend shows bullish momentum. "
        "Key support is at $150 and resistance at $165. "
        "RSI(14) is at 62 indicating moderate strength with no overbought signal. "
        "MACD shows a bullish crossover. Volume is above 20-day average confirming the trend. "
        "Risk assessment: Moderate risk profile. Consider a stop-loss at $148."
    )
    yield {"event": "answer", "data": json.dumps({"type": "answer", "content": final_answer})}


@router.post("/advisor/chat")
async def advisor_chat(request: ChatRequest):
    return EventSourceResponse(_generate_thought_events())


@router.get("/admin/sources")
async def list_sources(role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    _require_admin(role=role, x_role=x_role)
    return {"sources": MOCK_SOURCES}


@router.post("/admin/sources")
async def add_source(source: SourceRequest, role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    _require_admin(role=role, x_role=x_role)
    new_source = {
        "id": str(len(MOCK_SOURCES) + 1),
        "name": source.name,
        "base_url": source.base_url,
        "crawler_type": source.crawler_type,
        "active": True,
    }
    MOCK_SOURCES.append(new_source)
    return {"source": new_source}


@router.patch("/admin/sources/{source_id}")
async def toggle_source(source_id: str, role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    _require_admin(role=role, x_role=x_role)
    for src in MOCK_SOURCES:
        if src["id"] == source_id:
            src["active"] = not src["active"]
            return {"source": src}
    raise HTTPException(status_code=404, detail="Source not found")


@router.delete("/admin/sources/{source_id}")
async def delete_source(source_id: str, role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    _require_admin(role=role, x_role=x_role)
    for src in MOCK_SOURCES:
        if src["id"] == source_id:
            src["active"] = False
            return {"source": src}
    raise HTTPException(status_code=404, detail="Source not found")


@router.get("/admin/wiki/{symbol}")
async def get_wiki_state(symbol: str):
    wiki = MOCK_WIKI.get(symbol.upper())
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found for symbol")
    return {"wiki": wiki}


@router.get("/admin/wiki/{symbol}/history")
async def get_wiki_history(symbol: str):
    wiki = MOCK_WIKI.get(symbol.upper())
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found for symbol")
    return {"symbol": symbol.upper(), "history": wiki["history"]}


@router.post("/admin/wiki/{symbol}/trigger")
async def trigger_synthesis(symbol: str, role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    _require_admin(role=role, x_role=x_role)
    wiki = MOCK_WIKI.get(symbol.upper())
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found for symbol")
    wiki["version"] += 1
    wiki["history"].append({
        "version": wiki["version"],
        "timestamp": "2026-05-06T17:00:00Z",
        "source": "synthesis_agent",
    })
    return {"wiki": wiki}
