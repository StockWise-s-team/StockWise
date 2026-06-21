import json
from unittest.mock import AsyncMock, MagicMock, patch

import aio_pika
import pytest

from app.rabbitmq.producer import RabbitMQProducer


class TestRabbitMQProducer:
    @pytest.mark.asyncio
    async def test_publish_uses_correct_exchange_and_routing_key(self):
        producer = RabbitMQProducer()

        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        producer.connection = mock_connection
        producer.channel = mock_channel

        test_data = {
            "symbols": ["VNM", "HPG"],
            "source": "vnstock",
            "timestamp": "2026-05-31T02:00:00Z",
            "record_count": 2,
            "action": "price.updated",
        }

        await producer.publish("market.exchange", "price.updated", test_data)

        mock_channel.declare_exchange.assert_called_once_with(
            "market.exchange", aio_pika.ExchangeType.TOPIC, durable=True
        )
        mock_exchange.publish.assert_called_once()
        call = mock_exchange.publish.call_args
        body = json.loads(call.args[0].body.decode())
        assert body["symbols"] == ["VNM", "HPG"]
        assert body["action"] == "price.updated"

    @pytest.mark.asyncio
    async def test_publish_connects_lazily_if_not_connected(self):
        producer = RabbitMQProducer()
        producer.connection = None
        producer.channel = None

        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_channel = AsyncMock()
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        mock_exchange = AsyncMock()
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)

        with patch(
            "app.rabbitmq.producer.aio_pika.connect_robust",
            new_callable=AsyncMock,
            return_value=mock_connection,
        ) as mock_connect:
            await producer.publish("news.exchange", "raw.ingested", {"action": "raw.ingested"})

        mock_connect.assert_awaited_once()
        mock_channel.declare_exchange.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_cleans_up_connection(self):
        producer = RabbitMQProducer()
        mock_connection = AsyncMock()
        mock_connection.is_closed = False
        mock_channel = MagicMock()
        producer.connection = mock_connection
        producer.channel = mock_channel

        await producer.close()

        mock_connection.close.assert_awaited_once()
        assert producer.connection is None
        assert producer.channel is None

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self):
        producer = RabbitMQProducer()
        producer.connection = None
        producer.channel = None

        await producer.close()

        assert producer.connection is None
        assert producer.channel is None

    @pytest.mark.asyncio
    async def test_publish_serializes_all_types(self):
        producer = RabbitMQProducer()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)
        mock_connection = MagicMock()
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        producer.connection = mock_connection
        producer.channel = mock_channel
        mock_connection.is_closed = False

        await producer.publish(
            "market.exchange",
            "price.updated",
            {"record_count": 5, "symbols": [], "timestamp": None},
        )

        call = mock_exchange.publish.call_args
        body = json.loads(call.args[0].body.decode())
        assert body["record_count"] == 5
        assert body["symbols"] == []

    @pytest.mark.asyncio
    async def test_publish_message_body_contains_all_required_fields(self):
        producer = RabbitMQProducer()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)
        mock_connection = MagicMock()
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        producer.connection = mock_connection
        producer.channel = mock_channel
        mock_connection.is_closed = False

        test_data = {
            "symbols": ["VNM"],
            "source": "cafef",
            "timestamp": "2026-05-31T03:00:00Z",
            "record_count": 10,
            "action": "raw.ingested",
        }

        await producer.publish("news.exchange", "raw.ingested", test_data)

        call = mock_exchange.publish.call_args
        message = call.args[0]
        assert isinstance(message.body, bytes)
        body = json.loads(message.body.decode())
        assert body["symbols"] == ["VNM"]
        assert body["source"] == "cafef"
        assert body["record_count"] == 10
        assert body["action"] == "raw.ingested"
        assert body["timestamp"] == "2026-05-31T03:00:00Z"
