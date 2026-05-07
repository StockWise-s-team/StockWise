import json
import aio_pika
from app.config import settings

class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASS,
            )
            self.channel = await self.connection.channel()

    async def publish(self, exchange_name: str, routing_key: str, data: dict):
        if not self.channel:
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
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
