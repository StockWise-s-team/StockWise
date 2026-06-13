import asyncio
from typing import Any, Optional

from pydantic import BaseModel

from app.models.schemas import Citation, FinalAnswer, SSEEnvelope


class SSEEvent(BaseModel):
    """Represents a single SSE event to be sent to the client."""
    event: str
    data: str


class SSEManager:
    """Manages SSE event emission via an asyncio.Queue.

    Nodes push events to this manager; the SSE endpoint reads from the queue
    and yields ServerSentEvent objects to the HTTP response.
    """

    def __init__(self, session_id: str = "") -> None:
        self.queue: asyncio.Queue[Optional[SSEEvent]] = asyncio.Queue()
        self.session_id = session_id
        self._sequence = 0
        self._closed = False

    async def emit(self, event_type: str, data: dict[str, Any]) -> None:
        if self._closed:
            return
        self._sequence += 1
        envelope = SSEEnvelope(
            type=event_type,
            data=data,
            session_id=self.session_id,
            sequence=self._sequence,
        )
        await self.queue.put(
            SSEEvent(event=event_type, data=envelope.model_dump_json())
        )

    async def emit_thought(self, message: str, node: str = "") -> None:
        """Emit a thought event indicating agent progress."""
        await self.emit("thought", {"message": message, "node": node})

    async def emit_tool_call(self, tool_name: str, tool_input: dict[str, Any], status: str = "started") -> None:
        """Emit a tool_call event when a tool starts/finishes execution."""
        await self.emit("tool_call", {"tool": tool_name, "input": tool_input, "status": status})

    async def emit_tool_result(self, tool_name: str, summary: str, status: str = "completed") -> None:
        await self.emit("tool_result", {"tool": tool_name, "summary": summary, "status": status})

    async def emit_token(self, token: str) -> None:
        """Emit a single LLM token for streaming."""
        await self.emit("token", {"token": token})

    async def emit_chart_data(self, chart_data: dict[str, Any]) -> None:
        """Emit chart data for frontend rendering."""
        await self.emit("chart_data", chart_data)

    async def emit_final(
        self,
        answer: str,
        citations: Optional[list[Citation]] = None,
        intent: str = "",
        symbols: Optional[list[str]] = None,
        risk_flags: Optional[list[str]] = None,
        has_disclaimer: bool = False,
        data_mode: str = "live",
        data_freshness: Optional[dict[str, str | None]] = None,
    ) -> None:
        """Emit the final answer event."""
        payload = FinalAnswer(
            answer=answer,
            citations=citations or [],
            intent=intent,
            symbols=symbols or [],
            risk_flags=risk_flags or [],
            has_disclaimer=has_disclaimer,
            data_mode="demo" if data_mode == "demo" else "live",
            data_freshness=data_freshness or {},
        )
        await self.emit("final", payload.model_dump(mode="json"))

    async def emit_error(self, message: str, code: str, retryable: bool = False) -> None:
        """Emit an error event."""
        await self.emit("error", {"message": message, "code": code, "retryable": retryable})

    async def close(self) -> None:
        """Signal the end of the stream with a sentinel value."""
        if self._closed:
            return
        self._closed = True
        await self.queue.put(None)
