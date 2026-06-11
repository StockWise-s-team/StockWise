package com.stockwise.market.messaging;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.websocket.WebSocketSessionRegistry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component
@RequiredArgsConstructor
public class MarketDataConsumer {

    private final ObjectMapper objectMapper;
    private final SimpMessagingTemplate messagingTemplate;
    private final WebSocketSessionRegistry sessionRegistry;

    // Store-and-forward: last known price per symbol
    private final Map<String, LatestPriceResponse> lastKnownPrice = new ConcurrentHashMap<>();

    @RabbitListener(
            queues = "market_service_price_q",
            ackMode = org.springframework.amqp.rabbit.listener.AcknowledgeMode.AUTO,
            concurrency = "1"
    )
    public void consumePriceUpdate(String message) {
        try {
            Map<String, Object> payload = objectMapper.readValue(message, new com.fasterxml.jackson.core.type.TypeReference<>() {});

            String symbol = parseString(payload.get("symbol"));
            if (symbol == null || symbol.isBlank()) {
                log.warn("Price update message missing 'symbol' field, skipping: {}", message);
                return;
            }
            symbol = symbol.trim().toUpperCase();

            LatestPriceResponse priceData = buildResponse(payload, symbol);

            // Always store the latest price (store-and-forward for late subscribers)
            lastKnownPrice.put(symbol, priceData);

            // Always send to WebSocket if there are active sessions
            if (!sessionRegistry.getSessionsForSymbol(symbol).isEmpty()) {
                String destination = "/topic/price/" + symbol;
                messagingTemplate.convertAndSend(destination, priceData);
                log.info(
                        "Pushed price update for {} (close={}, change={}) to {}",
                        symbol,
                        priceData.close(),
                        priceData.change(),
                        destination
                );
            } else {
                log.debug(
                        "No active WebSocket sessions for {}, cached price for later delivery (close={})",
                        symbol,
                        priceData.close()
                );
            }

        } catch (JsonProcessingException ex) {
            log.warn("Failed to parse price update message: {}", message, ex);
        } catch (Exception ex) {
            log.warn("Failed to push price update: {}", ex.getMessage(), ex);
        }
    }

    /**
     * Deliver the cached latest price to a newly registered session,
     * so the client gets immediate data instead of waiting for the next pipeline run.
     */
    public LatestPriceResponse getCachedPrice(String symbol) {
        return lastKnownPrice.get(symbol.trim().toUpperCase());
    }

    private LatestPriceResponse buildResponse(Map<String, Object> payload, String symbol) {
        BigDecimal close     = parseDecimal(payload.get("close"));
        BigDecimal price     = close;  // message carries EOD data; price = close for daily bars
        BigDecimal open      = parseDecimal(payload.get("open"));
        BigDecimal high      = parseDecimal(payload.get("high"));
        BigDecimal low       = parseDecimal(payload.get("low"));
        Long volume          = parseLong(payload.get("volume"));
        BigDecimal change        = parseDecimal(payload.get("change"));
        BigDecimal changePercent = parseDecimal(payload.get("changePercent"));

        String tradeDateStr = parseString(payload.get("tradeDate"));
        LocalDate tradeDate = parseDate(tradeDateStr);

        return new LatestPriceResponse(
                symbol,
                price,
                open,
                high,
                low,
                close,
                volume,
                change,
                changePercent,
                tradeDate,
                Instant.now()
        );
    }

    private String parseString(Object value) {
        if (value == null) return null;
        return String.valueOf(value);
    }

    private BigDecimal parseDecimal(Object value) {
        if (value == null) return BigDecimal.ZERO;
        try {
            return new BigDecimal(String.valueOf(value));
        } catch (NumberFormatException e) {
            log.warn("Cannot parse decimal from '{}', using 0", value);
            return BigDecimal.ZERO;
        }
    }

    private Long parseLong(Object value) {
        if (value == null) return 0L;
        try {
            return Long.valueOf(String.valueOf(value));
        } catch (NumberFormatException e) {
            log.warn("Cannot parse long from '{}', using 0", value);
            return 0L;
        }
    }

    private LocalDate parseDate(String value) {
        if (value == null || value.isBlank()) return LocalDate.now();
        try {
            return LocalDate.parse(value);
        } catch (Exception e) {
            log.warn("Cannot parse date '{}', using today", value);
            return LocalDate.now();
        }
    }
}
