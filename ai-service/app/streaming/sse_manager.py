import asyncio
import json
from typing import Optional

from pydantic import BaseModel


class SSEEvent(BaseModel):
    """Represents a single SSE event to be sent to the client."""
    event: str
    data: str


class SSEManager:
    """Manages SSE event emission via an asyncio.Queue.

    Nodes push events to this manager; the SSE endpoint reads from the queue
    and yields ServerSentEvent objects to the HTTP response.
    """

    def __init__(self) -> None:
        self.queue: asyncio.Queue[Optional[SSEEvent]] = asyncio.Queue()

    async def emit_thought(self, message: str, node: str = "") -> None:
        """Emit a thought event indicating agent progress."""
        await self.queue.put(
            SSEEvent(
                event="thought",
                data=json.dumps({
                    "message": message,
                    "node": node,
                }),
            )
        )

    async def emit_tool_call(self, tool_name: str, tool_input: dict, status: str = "running") -> None:
        """Emit a tool_call event when a tool starts/finishes execution."""
        await self.queue.put(
            SSEEvent(
                event="tool_call",
                data=json.dumps({
                    "tool": tool_name,
                    "input": tool_input,
                    "status": status,
                }),
            )
        )

    async def emit_token(self, token: str) -> None:
        """Emit a single LLM token for streaming."""
        await self.queue.put(
            SSEEvent(
                event="token",
                data=json.dumps({"token": token}),
            )
        )

    async def emit_chart_data(self, chart_data: dict) -> None:
        """Emit chart data for frontend rendering."""
        await self.queue.put(
            SSEEvent(
                event="chart_data",
                data=json.dumps(chart_data),
            )
        )

    async def emit_final(self, answer: str, citations: Optional[list[str]] = None,
                         intent: str = "", symbols: Optional[list[str]] = None,
                         has_disclaimer: bool = False) -> None:
        """Emit the final answer event."""
        await self.queue.put(
            SSEEvent(
                event="final",
                data=json.dumps({
                    "answer": answer,
                    "citations": citations or [],
                    "intent": intent,
                    "symbols": symbols or [],
                    "has_disclaimer": has_disclaimer,
                }),
            )
        )

    async def emit_error(self, message: str, code: str) -> None:
        """Emit an error event."""
        await self.queue.put(
            SSEEvent(
                event="error",
                data=json.dumps({
                    "message": message,
                    "code": code,
                }),
            )
        )

    async def close(self) -> None:
        """Signal the end of the stream with a sentinel value."""
        await self.queue.put(None)
