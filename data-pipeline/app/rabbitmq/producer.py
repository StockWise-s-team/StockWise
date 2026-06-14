import json
import logging
import aio_pika
from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        if self.connection and not self.connection.is_closed:
            return
        self.connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASS,
        )
        self.channel = await self.connection.channel()

    async def reconnect(self):
        """Đóng connection cũ (nếu có) rồi kết nối lại."""
        logger.info("[RabbitMQProducer] Reconnecting...")
        await self.close()
        await self.connect()
        logger.info("[RabbitMQProducer] Reconnected successfully")

    async def publish(self, exchange_name: str, routing_key: str, data: dict):
        if not self.channel or self.connection.is_closed:
            await self.connect()

        exchange = await self.channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await exchange.publish(message, routing_key=routing_key)

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
        self.connection = None
        self.channel = None
