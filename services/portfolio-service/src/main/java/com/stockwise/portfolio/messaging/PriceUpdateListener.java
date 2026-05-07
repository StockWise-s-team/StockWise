package com.stockwise.portfolio.messaging;

import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class PriceUpdateListener {

    @RabbitListener(queues = "portfolio_service_price_q")
    public void onPriceUpdate(String message) {
        log.info("Received price update for portfolio valuation via RabbitMQ: {}", message);
    }
}
