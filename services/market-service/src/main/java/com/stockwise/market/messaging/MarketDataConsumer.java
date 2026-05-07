package com.stockwise.market.messaging;

import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class MarketDataConsumer {

    @RabbitListener(queues = "market_service_price_q")
    public void consumePriceUpdate(String message) {
        log.info("Received price update from RabbitMQ: {}", message);
    }
}
