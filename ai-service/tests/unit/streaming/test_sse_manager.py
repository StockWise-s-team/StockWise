import asyncio
import json
import pytest

from app.streaming.sse_manager import SSEManager, SSEEvent


class TestSSEManager:
    """Unit tests for SSEManager event emission."""

    @pytest.mark.asyncio
    async def test_emit_thought(self):
        """Thought event is queued with correct format."""
        manager = SSEManager()
        await manager.emit_thought("Đang phân tích...", node="router")

        event = await manager.queue.get()
        assert event is not None
        assert event.event == "thought"
        data = json.loads(event.data)
        assert data["message"] == "Đang phân tích..."
        assert data["node"] == "router"

    @pytest.mark.asyncio
    async def test_emit_tool_call(self):
        """Tool call event is queued with correct format."""
        manager = SSEManager()
        await manager.emit_tool_call("wiki_reader", {"symbol": "FPT"}, status="running")

        event = await manager.queue.get()
        assert event.event == "tool_call"
        data = json.loads(event.data)
        assert data["tool"] == "wiki_reader"
        assert data["input"] == {"symbol": "FPT"}
        assert data["status"] == "running"

    @pytest.mark.asyncio
    async def test_emit_token(self):
        """Token event is queued with correct format."""
        manager = SSEManager()
        await manager.emit_token("Xin")

        event = await manager.queue.get()
        assert event.event == "token"
        data = json.loads(event.data)
        assert data["token"] == "Xin"

    @pytest.mark.asyncio
    async def test_emit_chart_data(self):
        """Chart data event is queued with correct format."""
        manager = SSEManager()
        chart = {"chart_type": "line", "symbol": "FPT", "data": [1, 2, 3]}
        await manager.emit_chart_data(chart)

        event = await manager.queue.get()
        assert event.event == "chart_data"
        data = json.loads(event.data)
        assert data["chart_type"] == "line"

    @pytest.mark.asyncio
    async def test_emit_final(self):
        """Final event is queued with correct format."""
        manager = SSEManager()
        await manager.emit_final(
            answer="FPT đang tăng",
            citations=["https://cafef.vn"],
            intent="STOCK_OVERVIEW",
            symbols=["FPT"],
            has_disclaimer=True,
        )

        event = await manager.queue.get()
        assert event.event == "final"
        data = json.loads(event.data)
        assert data["answer"] == "FPT đang tăng"
        assert data["has_disclaimer"] is True
        assert "https://cafef.vn" in data["citations"]

    @pytest.mark.asyncio
    async def test_emit_error(self):
        """Error event is queued with correct format."""
        manager = SSEManager()
        await manager.emit_error("LLM không khả dụng", "LLM_UNAVAILABLE")

        event = await manager.queue.get()
        assert event.event == "error"
        data = json.loads(event.data)
        assert data["message"] == "LLM không khả dụng"
        assert data["code"] == "LLM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_close_sends_sentinel(self):
        """Close sends None sentinel to end the stream."""
        manager = SSEManager()
        await manager.close()

        event = await manager.queue.get()
        assert event is None

    @pytest.mark.asyncio
    async def test_event_order_preserved(self):
        """Events are dequeued in the order they were emitted."""
        manager = SSEManager()
        await manager.emit_thought("thought 1")
        await manager.emit_thought("thought 2")
        await manager.emit_final("answer")
        await manager.close()

        events = []
        while True:
            event = await manager.queue.get()
            if event is None:
                break
            events.append(event.event)

        assert events == ["thought", "thought", "final"]
