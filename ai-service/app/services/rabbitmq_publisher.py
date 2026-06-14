import logging

from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    async def publish_synthesis_requested(self, symbol: str) -> bool:
        if not settings.AI_RABBITMQ_ENABLED:
            return False
        try:
            import aio_pika

            connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASS,
                timeout=3,
            )
            async with connection:
                channel = await connection.channel()
                exchange = await channel.declare_exchange("wiki.exchange", durable=True)
                await exchange.publish(
                    aio_pika.Message(body=symbol.upper().encode("utf-8")),
                    routing_key="synthesis.requested",
                )
            return True
        except Exception as exc:
            logger.warning("RabbitMQ synthesis delivery failed: %s", exc)
            return False
