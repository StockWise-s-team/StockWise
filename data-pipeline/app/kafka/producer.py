from kafka import KafkaProducer
import json
from app.config import settings
from app.kafka.topics import MARKET_PRICE_UPDATED_TOPIC, NEWS_RAW_INGESTED_TOPIC

class KafkaEventProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def publish_price_update(self, data: dict):
        self.producer.send(MARKET_PRICE_UPDATED_TOPIC, value=data)

    def publish_news_ingested(self, data: dict):
        self.producer.send(NEWS_RAW_INGESTED_TOPIC, value=data)

    def close(self):
        self.producer.flush()
        self.producer.close()
