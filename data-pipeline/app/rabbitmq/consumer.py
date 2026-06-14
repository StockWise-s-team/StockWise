"""
rabbitmq/consumer.py
====================
Helper dùng để peek message từ RabbitMQ exchange mà không cần queue có sẵn.

Chiến lược:
  1. Tạo queue tạm, auto_delete=True, exclusive=False
  2. Bind queue với exchange + routing_key
  3. Polling message mỗi 1s cho tới khi có message hoặc hết timeout
  4. Lấy message ra, REQUEUE lại (không ack) — để message vẫn đến consumer thật
  5. Cleanup queue
"""
import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 45
POLL_INTERVAL_SECONDS = 1


class RabbitPeeker:
    """Tạo queue tạm, bind, đợi message, lấy về rồi cleanup."""

    def __init__(self):
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractRobustChannel] = None

    async def connect(self) -> None:
        if self._connection and not self._connection.is_closed:
            return
        self._connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASS,
        )
        self._channel = await self._connection.channel()

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None

    async def peek(
        self,
        exchange_name: str,
        routing_key: str,
        max_messages: int = 1,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Tạo queue tạm, bind, đợi tối đa `timeout_seconds` để lấy tối đa
        `max_messages` message. Trả về (list_message, queue_name).
        Message được nack-requeue=True để consumer thật (market/portfolio service)
        vẫn nhận được.
        """
        await self.connect()
        assert self._channel is not None

        queue_name = f"peek_{int(time.time() * 1000)}"
        queue = await self._channel.declare_queue(
            queue_name,
            durable=False,
            exclusive=False,
            auto_delete=True,
        )
        # Đảm bảo exchange tồn tại (idempotent — nếu chưa có, declare topic durable)
        exchange = await self._channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )
        await queue.bind(exchange, routing_key=routing_key)

        logger.info(
            "[RabbitPeeker] Temp queue '%s' bound to %s/%s — waiting up to %ds for %d message(s)",
            queue_name, exchange_name, routing_key, timeout_seconds, max_messages,
        )

        results: List[Dict[str, Any]] = []
        deadline = time.monotonic() + timeout_seconds

        try:
            while len(results) < max_messages and time.monotonic() < deadline:
                # Thử lấy message không chờ (no-wait=False nhưng timeout ngắn)
                msg = await queue.get(timeout=POLL_INTERVAL_SECONDS, fail=False)
                if msg is None:
                    continue
                async with msg.process(requeue=True, ignore_processed=True):
                    # msg.process() với requeue=True sẽ requeue khi context exit
                    # — đảm bảo consumer thật (nếu bind) vẫn nhận được
                    try:
                        body = msg.body.decode("utf-8")
                        payload = json.loads(body) if body else {}
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        payload = {"_decode_error": str(exc), "_raw": msg.body[:500].decode("utf-8", errors="replace")}
                    results.append({
                        "routing_key": msg.routing_key or routing_key,
                        "exchange": msg.exchange or exchange_name,
                        "payload": payload,
                        "payload_size_bytes": len(msg.body),
                        "redelivered": msg.redelivered,
                    })
            return results, queue_name
        finally:
            try:
                await queue.delete(if_unused=False, if_empty=False)
            except Exception as exc:
                logger.warning("[RabbitPeeker] Failed to delete temp queue: %s", exc)
