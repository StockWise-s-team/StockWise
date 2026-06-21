package com.stockwise.market.messaging;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.websocket.WebSocketSessionRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class MarketDataConsumer {


    private static final Logger log = LoggerFactory.getLogger(MarketDataConsumer.class);

    private final ObjectMapper objectMapper;
    private final SimpMessagingTemplate messagingTemplate;
    private final WebSocketSessionRegistry sessionRegistry;

    private final Map<String, LatestPriceResponse> lastKnownPrice = new ConcurrentHashMap<>();

    public MarketDataConsumer(ObjectMapper objectMapper,
                             SimpMessagingTemplate messagingTemplate,
                             WebSocketSessionRegistry sessionRegistry) {
        this.objectMapper = objectMapper;
        this.messagingTemplate = messagingTemplate;
        this.sessionRegistry = sessionRegistry;
    }

    @RabbitListener(queues = "market_service_price_q")
    public void consumePriceUpdate(String message) {
        try {
            Map<String, Object> payload = objectMapper.readValue(
                    message, new TypeReference<Map<String, Object>>() {}
            );

            List<Map<String, Object>> priceRecords = extractPriceRecords(payload);
            if (priceRecords.isEmpty()) {
                String singleSymbol = parseString(payload.get("symbol"));
                if (singleSymbol != null && !singleSymbol.isBlank()) {
                    Map<String, Object> single = new LinkedHashMap<>();
                    single.put("symbol", singleSymbol);
                    copyIfPresent(payload, single,
                            "close", "open", "high", "low", "volume",
                            "change", "changePercent", "price_change", "percent_change",
                            "reference_price", "average_price", "ceiling_price", "floor_price",
                            "timestamp", "tradeDate");
                    priceRecords.add(single);
                }
            }

            for (Map<String, Object> rec : priceRecords) {
                String symbol = parseString(rec.get("symbol"));
                if (symbol == null || symbol.isBlank()) {
                    log.warn("Price update record missing 'symbol' field, skipping: {}", rec);
                    continue;
                }
                symbol = symbol.trim().toUpperCase();

                LatestPriceResponse priceData = buildResponse(rec, symbol);
                lastKnownPrice.put(symbol, priceData);

                if (!sessionRegistry.getSessionsForSymbol(symbol).isEmpty()) {
                    String destination = "/topic/price/" + symbol;
                    messagingTemplate.convertAndSend(destination, priceData);
                    log.info(
                            "Pushed price update for {} (close={}, change={}) to {}",
                            symbol, priceData.close(), priceData.change(), destination
                    );
                } else {
                    log.debug(
                            "No active WebSocket sessions for {}, cached price for later delivery (close={})",
                            symbol, priceData.close()
                    );
                }
            }
        } catch (JsonProcessingException ex) {
            log.warn("Failed to parse price update message: {}", message, ex);
        } catch (Exception ex) {
            log.warn("Failed to push price update: {}", ex.getMessage(), ex);
        }
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> extractPriceRecords(Map<String, Object> payload) {
        Object prices = payload.get("prices");
        if (prices instanceof List<?> list) {
            List<Map<String, Object>> out = new ArrayList<>();
            for (Object item : list) {
                if (item instanceof Map<?, ?> m) {
                    out.add((Map<String, Object>) m);
                }
            }
            return out;
        }
        return List.of();
    }

    public LatestPriceResponse getCachedPrice(String symbol) {
        return lastKnownPrice.get(symbol.trim().toUpperCase());
    }

    public Map<String, LatestPriceResponse> getCachedPrices(Collection<String> symbols) {
        Map<String, LatestPriceResponse> out = new HashMap<>();
        for (String sym : symbols) {
            if (sym == null || sym.isBlank()) continue;
            LatestPriceResponse cached = lastKnownPrice.get(sym.trim().toUpperCase());
            if (cached != null) {
                out.put(sym.toUpperCase(), cached);
            }
        }
        return out;
    }

    private LatestPriceResponse buildResponse(Map<String, Object> payload, String symbol) {
        BigDecimal close = parseDecimal(payload.get("close"));
        BigDecimal price = close != null ? close : BigDecimal.ZERO;
        BigDecimal open = parseDecimal(payload.get("open"));
        BigDecimal high = parseDecimal(payload.get("high"));
        BigDecimal low = parseDecimal(payload.get("low"));
        Long volume = parseLong(payload.get("volume"));

        BigDecimal change = parseDecimal(firstNonNull(
                payload.get("change"), payload.get("price_change")));
        if (change == null) change = BigDecimal.ZERO;

        BigDecimal changePercent = parseDecimal(firstNonNull(
                payload.get("changePercent"), payload.get("percent_change")));
        if (changePercent == null) changePercent = BigDecimal.ZERO;

        String tradeDateStr = parseString(firstNonNull(
                payload.get("tradeDate"), payload.get("timestamp")));
        LocalDate tradeDate = parseDate(tradeDateStr);

        return new LatestPriceResponse(
                symbol,
                price,
                open,
                high,
                low,
                close != null ? close : BigDecimal.ZERO,
                volume,
                change,
                changePercent,
                tradeDate,
                Instant.now()
        );
    }

    private static Object firstNonNull(Object... values) {
        for (Object v : values) {
            if (v != null) return v;
        }
        return null;
    }

    private static void copyIfPresent(Map<String, Object> src, Map<String, Object> dst, String... keys) {
        for (String k : keys) {
            if (src.containsKey(k) && src.get(k) != null) {
                dst.put(k, src.get(k));
            }
        }
    }

    private String parseString(Object value) {
        if (value == null) return null;
        return String.valueOf(value);
    }

    private BigDecimal parseDecimal(Object value) {
        if (value == null) return null;
        try {
            return new BigDecimal(String.valueOf(value));
        } catch (NumberFormatException e) {
            log.warn("Cannot parse decimal from '{}'", value);
            return null;
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
        } catch (DateTimeParseException e) {
            try {
                return OffsetDateTime.parse(value).toLocalDate();
            } catch (DateTimeParseException e2) {
                log.warn("Cannot parse date '{}', using today", value);
                return LocalDate.now();
            }
        }
    }
}
