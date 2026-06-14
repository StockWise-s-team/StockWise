from datetime import datetime, timezone
import sys
from types import ModuleType
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

if "sse_starlette.sse" not in sys.modules:
    sse_module = ModuleType("sse_starlette.sse")
    sse_module.EventSourceResponse = object
    sse_module.ServerSentEvent = object
    sys.modules.setdefault("sse_starlette", ModuleType("sse_starlette"))
    sys.modules["sse_starlette.sse"] = sse_module

from app.api.v1.endpoints import advisor


class FakeChatRepository:
    def __init__(self, db):
        self.db = db

    async def list_sessions(self, user_id: str):
        return [
            SimpleNamespace(
                id=uuid4(),
                user_id=user_id,
                title="First question",
                created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
                updated_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
            )
        ]

    async def list_messages_for_user(self, session_id: str, user_id: str):
        if session_id == "forbidden":
            raise PermissionError("not owned")
        return [
            SimpleNamespace(
                id=uuid4(),
                session_id=uuid4(),
                role="user",
                content="Review FPT",
                message_metadata={},
                created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
            )
        ]

    async def delete_session(self, session_id: str, user_id: str):
        return session_id == "owned"


class FakeContentRepository:
    def __init__(self, db):
        self.db = db

    async def get_wiki(self, symbol: str):
        return {"symbol": symbol.upper(), "version": 1}

    async def get_wiki_history(self, symbol: str):
        return [{"symbol": symbol.upper(), "version": 1}]


@pytest.mark.asyncio
async def test_list_advisor_sessions_maps_current_user_sessions(monkeypatch):
    monkeypatch.setattr(advisor, "ChatRepository", FakeChatRepository)

    response = await advisor.list_advisor_sessions(user_id="user-1", db=object())

    assert len(response) == 1
    assert response[0].title == "First question"
    assert response[0].id


@pytest.mark.asyncio
async def test_list_advisor_messages_hides_non_owned_session(monkeypatch):
    monkeypatch.setattr(advisor, "ChatRepository", FakeChatRepository)

    with pytest.raises(HTTPException) as exc:
        await advisor.list_advisor_session_messages("forbidden", user_id="user-1", db=object())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_advisor_session_hides_non_owned_session(monkeypatch):
    monkeypatch.setattr(advisor, "ChatRepository", FakeChatRepository)

    with pytest.raises(HTTPException) as exc:
        await advisor.delete_advisor_session("missing", user_id="user-1", db=object())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_admin_wiki_state_requires_admin_role(monkeypatch):
    monkeypatch.setattr(advisor, "ContentRepository", FakeContentRepository)

    with pytest.raises(HTTPException) as exc:
        await advisor.get_wiki_state("FPT", db=object())

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_admin_wiki_state_returns_data_for_admin(monkeypatch):
    monkeypatch.setattr(advisor, "ContentRepository", FakeContentRepository)

    response = await advisor.get_wiki_state("fpt", x_role="admin", db=object())

    assert response == {"wiki": {"symbol": "FPT", "version": 1}}


@pytest.mark.asyncio
async def test_trigger_synthesis_proxies_to_data_pipeline(monkeypatch):
    captured = {}

    async def fake_trigger(symbol: str):
        captured["symbol"] = symbol
        return {"status": "started", "symbols_processed": 0, "errors": []}

    monkeypatch.setattr(advisor, "_request_data_pipeline_synthesis", fake_trigger)

    response = await advisor.trigger_synthesis("fpt", x_role="admin")

    assert captured == {"symbol": "fpt"}
    assert response["status"] == "started"
    assert response["symbol"] == "FPT"
    assert response["pipeline"]["status"] == "started"
