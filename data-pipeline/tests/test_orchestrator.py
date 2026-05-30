import json
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.synthesis.orchestrator import SynthesisOrchestrator


def _make_async_cm():
    @asynccontextmanager
    async def cm():
        yield
    return cm()


class TestSynthesisOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        return SynthesisOrchestrator()

    @pytest.mark.asyncio
    async def test_start_creates_rabbitmq_connection(self, orchestrator):
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_queue = AsyncMock()

        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)
        mock_channel.declare_queue = AsyncMock(return_value=mock_queue)
        mock_queue.bind = AsyncMock()
        mock_queue.consume = AsyncMock()

        with patch(
            "app.synthesis.orchestrator.aio_pika.connect_robust",
            new_callable=AsyncMock,
            return_value=mock_conn,
        ):
            await orchestrator.start()

        mock_channel.set_qos.assert_awaited_once()
        mock_channel.declare_exchange.assert_called_once()
        mock_channel.declare_queue.assert_called_once()
        mock_queue.bind.assert_called_once()
        mock_queue.consume.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_parses_symbols_and_calls_synthesize(self, orchestrator):
        mock_agent = AsyncMock()
        mock_agent.synthesize = AsyncMock()

        message_body = {
            "symbols": ["VNM", "HPG"],
            "source": "cafef",
            "timestamp": "2026-05-31T00:00:00Z",
            "record_count": 1,
            "action": "raw.ingested",
        }

        mock_message = MagicMock()
        mock_message.body = json.dumps(message_body).encode()
        mock_message.process = MagicMock(return_value=AsyncMock())

        with patch(
            "app.synthesis.orchestrator.SynthesisAgent",
            return_value=mock_agent,
        ):
            with patch("app.synthesis.orchestrator.logger"):
                await orchestrator._on_message(mock_message)

        mock_agent.synthesize.assert_awaited_once_with(["VNM", "HPG"])

    @pytest.mark.asyncio
    async def test_on_message_handles_synthesis_error_gracefully(self, orchestrator):
        mock_agent = AsyncMock()
        mock_agent.synthesize = AsyncMock(side_effect=RuntimeError("Gemini failed"))

        message_body = {"symbols": ["VNM"], "source": "cafef", "action": "raw.ingested"}
        mock_message = MagicMock()
        mock_message.body = json.dumps(message_body).encode()
        mock_message.process = MagicMock(return_value=_make_async_cm())

        with patch(
            "app.synthesis.orchestrator.SynthesisAgent",
            return_value=mock_agent,
        ):
            with patch("app.synthesis.orchestrator.logger") as mock_logger:
                await orchestrator._on_message(mock_message)

        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_handles_invalid_json_gracefully(self, orchestrator):
        mock_message = MagicMock()
        mock_message.body = b"not json"
        mock_message.process = MagicMock(return_value=_make_async_cm())

        with patch("app.synthesis.orchestrator.logger") as mock_logger:
            await orchestrator._on_message(mock_message)

        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_on_message_skips_when_no_symbols(self, orchestrator):
        mock_agent = AsyncMock()

        message_body = {"symbols": [], "source": "cafef", "action": "raw.ingested"}
        mock_message = MagicMock()
        mock_message.body = json.dumps(message_body).encode()
        mock_message.process = MagicMock(return_value=AsyncMock())

        with patch(
            "app.synthesis.orchestrator.SynthesisAgent",
            return_value=mock_agent,
        ):
            with patch("app.synthesis.orchestrator.logger") as mock_logger:
                await orchestrator._on_message(mock_message)

        mock_agent.synthesize.assert_not_called()
        mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_close_cleans_up_resources(self, orchestrator):
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        orchestrator._connection = mock_conn
        orchestrator._channel = MagicMock()
        orchestrator._running = True

        await orchestrator.close()

        mock_conn.close.assert_awaited_once()
        assert orchestrator._connection is None
        assert orchestrator._channel is None
        assert orchestrator._running is False

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self, orchestrator):
        orchestrator._connection = None
        orchestrator._channel = None
        orchestrator._running = False

        await orchestrator.close()

        assert orchestrator._running is False

    @pytest.mark.asyncio
    async def test_start_raises_on_connection_failure(self, orchestrator):
        with patch(
            "app.synthesis.orchestrator.aio_pika.connect_robust",
            new_callable=AsyncMock,
            side_effect=Exception("Connection refused"),
        ):
            with pytest.raises(Exception, match="Connection refused"):
                await orchestrator.start()
