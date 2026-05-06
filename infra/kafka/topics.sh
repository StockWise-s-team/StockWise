#!/bin/bash
KAFKA_BIN="/usr/bin/kafka-topics"
BOOTSTRAP="kafka:9092"

TOPICS=(
    "market.price.updated"
    "news.raw.ingested"
    "portfolio.updated"
    "wiki.synthesis.requested"
)

for TOPIC in "${TOPICS[@]}"; do
    $KAFKA_BIN --bootstrap-server $BOOTSTRAP --create --if-not-exists --topic "$TOPIC" --partitions 3 --replication-factor 1
    echo "Created topic: $TOPIC"
done
