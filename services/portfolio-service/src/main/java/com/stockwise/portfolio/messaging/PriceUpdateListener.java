package com.stockwise.portfolio.messaging;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockwise.portfolio.application.service.order.OrderMatchProcessor;
import com.stockwise.portfolio.application.service.order.validation.SymbolPriceCache;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Slf4j
@Component
@RequiredArgsConstructor
public class PriceUpdateListener {

    private final ObjectMapper objectMapper;
    private final SymbolPriceCache symbolPriceCache;
    private final OrderMatchProcessor orderMatchProcessor;

    @RabbitListener(queues = "portfolio_service_price_q")
    public void onPriceUpdate(String message) {
        log.info("Received price update message: {}", message);
        try {
            JsonNode jsonNode = objectMapper.readTree(message);
            if (!jsonNode.has("symbol")) {
                log.warn("Price update message missing 'symbol': {}", message);
                return;
            }

            String symbol = jsonNode.get("symbol").asText().trim().toUpperCase();
            BigDecimal price = extractPrice(jsonNode);

            if (price == null || price.compareTo(BigDecimal.ZERO) <= 0) {
                log.warn("Could not extract a valid price for symbol {} from message: {}", symbol, message);
                return;
            }

            log.info("Updating local cache for symbol {} with latest price {}", symbol, price);

            // 1. Update local cache
            symbolPriceCache.put(symbol, price);

            // 2. Delegate matching logic to OrderMatchProcessor (SRP compliant)
            orderMatchProcessor.matchPendingOrders(symbol, price);

        } catch (Exception e) {
            log.error("Error processing price update RabbitMQ message: {}", e.getMessage(), e);
        }
    }

    private BigDecimal extractPrice(JsonNode jsonNode) {
        if (jsonNode.has("price")) {
            return new BigDecimal(jsonNode.get("price").asText());
        }
        if (jsonNode.has("close")) {
            return new BigDecimal(jsonNode.get("close").asText());
        }
        if (jsonNode.has("latestPrice")) {
            return new BigDecimal(jsonNode.get("latestPrice").asText());
        }
        if (jsonNode.has("prices") && jsonNode.get("prices").isArray() && jsonNode.get("prices").size() > 0) {
            JsonNode priceNode = jsonNode.get("prices").get(0);
            if (priceNode.has("close")) {
                return new BigDecimal(priceNode.get("close").asText());
            }
            if (priceNode.has("price")) {
                return new BigDecimal(priceNode.get("price").asText());
            }
        }
        return null;
    }
}
