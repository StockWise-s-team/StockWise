import json

import pytest

from app.models.schemas import Citation
from app.streaming.sse_manager import SSEManager


class TestSSEManager:
    @pytest.mark.asyncio
    async def test_emit_thought(self):
        manager = SSEManager(session_id="session-1")
        await manager.emit_thought("Dang phan tich...", node="router")
        event = await manager.queue.get()
        envelope = json.loads(event.data)
        assert event.event == "thought"
        assert envelope["type"] == "thought"
        assert envelope["session_id"] == "session-1"
        assert envelope["sequence"] == 1
        assert envelope["data"] == {"message": "Dang phan tich...", "node": "router"}

    @pytest.mark.asyncio
    async def test_emit_tool_call_and_result(self):
        manager = SSEManager()
        await manager.emit_tool_call("wiki_reader", {"symbol": "FPT"})
        await manager.emit_tool_result("wiki_reader", "completed")
        call = json.loads((await manager.queue.get()).data)
        result = json.loads((await manager.queue.get()).data)
        assert call["data"]["tool"] == "wiki_reader"
        assert call["data"]["status"] == "started"
        assert result["type"] == "tool_result"

    @pytest.mark.asyncio
    async def test_emit_token(self):
        manager = SSEManager()
        await manager.emit_token("Xin")
        envelope = json.loads((await manager.queue.get()).data)
        assert envelope["data"]["token"] == "Xin"

    @pytest.mark.asyncio
    async def test_emit_chart_data(self):
        manager = SSEManager()
        await manager.emit_chart_data({"symbol": "FPT", "series": []})
        envelope = json.loads((await manager.queue.get()).data)
        assert envelope["data"]["symbol"] == "FPT"

    @pytest.mark.asyncio
    async def test_emit_final(self):
        manager = SSEManager()
        await manager.emit_final(
            answer="FPT dang tang",
            citations=[
                Citation(
                    source_type="news_article",
                    title="CafeF",
                    reference="news_articles:1",
                    url="https://cafef.vn",
                )
            ],
            intent="STOCK_OVERVIEW",
            symbols=["FPT"],
            has_disclaimer=True,
        )
        envelope = json.loads((await manager.queue.get()).data)
        assert envelope["data"]["answer"] == "FPT dang tang"
        assert envelope["data"]["citations"][0]["url"] == "https://cafef.vn"

    @pytest.mark.asyncio
    async def test_emit_error(self):
        manager = SSEManager()
        await manager.emit_error("LLM unavailable", "LLM_UNAVAILABLE")
        envelope = json.loads((await manager.queue.get()).data)
        assert envelope["data"]["code"] == "LLM_UNAVAILABLE"
        assert envelope["data"]["retryable"] is False

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self):
        manager = SSEManager()
        await manager.close()
        await manager.close()
        assert await manager.queue.get() is None
        assert manager.queue.empty()

    @pytest.mark.asyncio
    async def test_event_order_and_sequence_are_preserved(self):
        manager = SSEManager()
        await manager.emit_thought("thought 1")
        await manager.emit_thought("thought 2")
        await manager.emit_final("answer")
        await manager.close()
        envelopes = []
        while True:
            event = await manager.queue.get()
            if event is None:
                break
            envelopes.append(json.loads(event.data))
        assert [event["type"] for event in envelopes] == ["thought", "thought", "final"]
        assert [event["sequence"] for event in envelopes] == [1, 2, 3]
