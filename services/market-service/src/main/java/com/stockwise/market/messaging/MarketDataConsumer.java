package com.stockwise.market.messaging;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class MarketDataConsumer {

    private final ObjectMapper objectMapper;

    @RabbitListener(queues = "market_service_price_q")
    public void consumePriceUpdate(String message) {
        try {
            Map<String, Object> payload = objectMapper.readValue(message, new TypeReference<>() {});
            Object symbolsValue = payload.get("symbols");
            List<String> symbols = symbolsValue instanceof List<?> rawList
                    ? rawList.stream().map(String::valueOf).toList()
                    : List.of();

            log.info(
                    "Received market price update event: symbols={}, source={}, timestamp={}, action={}",
                    symbols,
                    payload.get("source"),
                    payload.get("timestamp"),
                    payload.get("action")
            );
        } catch (Exception ex) {
            log.warn("Failed to parse market price update event: {}", message, ex);
        }
    }
}
