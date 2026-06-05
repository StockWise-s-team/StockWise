import asyncio
import json
import logging
from typing import Optional

import aio_pika
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractConnection, AbstractChannel

from app.config import settings
from app.synthesis.synthesis_agent import SynthesisAgent

logger = logging.getLogger(__name__)

_EXCHANGE_NAME = "news.exchange"
_ROUTING_KEY = "raw.ingested"


class SynthesisOrchestrator:
    def __init__(self):
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._queue_name = "synthesis-orchestrator"
        self._running = False

    async def start(self) -> None:
        logger.info("[Orchestrator] Connecting to RabbitMQ at %s:%d",
                    settings.RABBITMQ_HOST, settings.RABBITMQ_PORT)
        self._connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASS,
        )
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)

        exchange = await self._channel.declare_exchange(
            _EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )

        queue = await self._channel.declare_queue(
            self._queue_name, durable=True
        )
        await queue.bind(exchange, routing_key=_ROUTING_KEY)

        await queue.consume(self._on_message)
        self._running = True
        logger.info(
            "[Orchestrator] Listening on %s / %s", _EXCHANGE_NAME, _ROUTING_KEY
        )

    async def _on_message(self, message: IncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                body = json.loads(message.body.decode())
                symbols = body.get("symbols", [])
                if not symbols:
                    logger.warning(
                        "[Orchestrator] Received message with no symbols: %s", body
                    )
                    return

                logger.info(
                    "[Orchestrator] Received synthesis trigger for symbols: %s", symbols
                )
                agent = SynthesisAgent()
                await agent.synthesize(symbols)
                logger.info(
                    "[Orchestrator] Completed synthesis for symbols: %s", symbols
                )
            except json.JSONDecodeError as e:
                logger.error("[Orchestrator] Failed to parse message: %s", e)
            except Exception as exc:
                logger.error(
                    "[Orchestrator] Synthesis failed: %s: %s",
                    type(exc).__name__, exc,
                )

    async def close(self) -> None:
        logger.info("[Orchestrator] Shutting down")
        self._running = False
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None
        logger.info("[Orchestrator] Shutdown complete")
