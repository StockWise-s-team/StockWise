package com.stockwise.portfolio.kafka;

import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class PriceUpdateListener {

    @KafkaListener(topics = "market.price.updated", groupId = "portfolio-service-group")
    public void onPriceUpdate(String message) {
        log.info("Received price update for portfolio valuation: {}", message);
    }
}
