package com.stockwise.market.kafka;

import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class MarketDataConsumer {

    @KafkaListener(topics = "market.price.updated", groupId = "market-service-group")
    public void consumePriceUpdate(String message) {
        log.info("Received price update from Kafka: {}", message);
    }
}
