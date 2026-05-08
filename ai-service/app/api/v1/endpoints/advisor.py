import asyncio
import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.database import get_db
from app.db.repositories.content_repo import ContentRepository
from app.db.repositories.market_repo import MarketRepository
from app.models.schemas import ChatRequest, SourceRequest

router = APIRouter()


def _require_admin(role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    resolved = role or x_role
    if resolved != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")


def _json_default(value: Any) -> str | float:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def _event(event_type: str, content: str) -> dict[str, str]:
    return {
        "event": event_type,
        "data": json.dumps({"type": event_type, "content": content}, default=_json_default),
    }


def _extract_symbol(message: str) -> str | None:
    candidates = re.findall(r"\b[A-Z]{2,10}\b", message.upper())
    ignored = {"AI", "CEO", "EPS", "PE", "PB", "ROE", "ROA", "RSI", "MACD"}
    return next((symbol for symbol in candidates if symbol not in ignored), None)


async def _generate_thought_events(message: str, db: AsyncSession):
    market_repo = MarketRepository(db)
    content_repo = ContentRepository(db)
    symbol = _extract_symbol(message)

    for thought in ("Analyzing your query...", "Checking available market and wiki context..."):
        yield _event("thought", thought)
        await asyncio.sleep(0.2)

    if not symbol:
        yield _event(
            "answer",
            "I could not identify a stock symbol in your question. Include a ticker such as FPT, VNM, VCB, or HPG so I can ground the answer in market/wiki data.",
        )
        return

    yield _event("thought", f"Loading latest context for {symbol}...")
    latest_price = await market_repo.get_latest_price(symbol)
    ratios = await market_repo.get_financial_ratios(symbol)
    wiki = await content_repo.get_wiki(symbol)

    if not latest_price and not ratios and not wiki:
        yield _event(
            "answer",
            f"I do not have database context for {symbol} yet. The data pipeline needs to seed or ingest market data, ratios, or company wiki information before I can give a grounded answer.",
        )
        return

    parts = [f"Grounded context for {symbol}:"]
    if latest_price:
        parts.append(
            "Latest price row: "
            f"close={latest_price.get('close')}, trade_date={latest_price.get('trade_date')}, "
            f"volume={latest_price.get('volume')}."
        )
    if ratios:
        latest_ratio = ratios[0]
        parts.append(
            "Latest ratios: "
            f"period={latest_ratio.get('period')}, PE={latest_ratio.get('pe_ratio')}, "
            f"PB={latest_ratio.get('pb_ratio')}, EPS={latest_ratio.get('eps')}, "
            f"ROE={latest_ratio.get('roe')}."
        )
    if wiki:
        wiki_data = wiki.get("wiki_data") or {}
        summary = wiki_data.get("summary") or wiki_data.get("overview")
        parts.append(
            f"Company wiki v{wiki.get('version')}: {summary or 'wiki exists, but no summary field is available yet'}."
        )
    parts.append(
        "Risk note: this is informational context for analysis, not a guaranteed return or trading instruction."
    )
    yield _event("answer", "\n".join(parts))


@router.post("/advisor/chat")
async def advisor_chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    return EventSourceResponse(_generate_thought_events(request.message, db))


@router.get("/advisor/chat/stream")
async def advisor_chat_stream(message: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    return EventSourceResponse(_generate_thought_events(message, db))


@router.get("/admin/sources")
async def list_sources(
    role: str = Header(None),
    x_role: str = Header(None, alias="X-Role"),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(role=role, x_role=x_role)
    return {"sources": await ContentRepository(db).list_sources()}


@router.post("/admin/sources")
async def add_source(
    source: SourceRequest,
    role: str = Header(None),
    x_role: str = Header(None, alias="X-Role"),
    db: AsyncSession = Depends(get_db),
):
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
    _require_admin(role=role, x_role=x_role)
    source = await ContentRepository(db).deactivate_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"source": source}


@router.get("/admin/wiki/{symbol}")
async def get_wiki_state(symbol: str, db: AsyncSession = Depends(get_db)):
    wiki = await ContentRepository(db).get_wiki(symbol)
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found for symbol")
    return {"wiki": wiki}


@router.get("/admin/wiki/{symbol}/history")
async def get_wiki_history(symbol: str, db: AsyncSession = Depends(get_db)):
    history = await ContentRepository(db).get_wiki_history(symbol)
    return {"symbol": symbol.upper(), "history": history}


@router.post("/admin/wiki/{symbol}/trigger")
async def trigger_synthesis(symbol: str, role: str = Header(None), x_role: str = Header(None, alias="X-Role")):
    _require_admin(role=role, x_role=x_role)
    return {
        "status": "accepted",
        "symbol": symbol.upper(),
        "message": "Synthesis trigger accepted by API. Queue-backed execution should be wired by the data-pipeline owner.",
    }
