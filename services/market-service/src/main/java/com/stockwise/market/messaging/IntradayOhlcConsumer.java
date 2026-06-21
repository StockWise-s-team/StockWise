package com.stockwise.market.messaging;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockwise.market.application.store.InMemoryIntradayBarStore;
import com.stockwise.market.application.store.IntradayBar;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
public class IntradayOhlcConsumer {

    private static final Logger log = LoggerFactory.getLogger(IntradayOhlcConsumer.class);
    private static final DateTimeFormatter BAR_TIME_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final ZoneOffset ICT_OFFSET = ZoneOffset.ofHours(7);

    private final ObjectMapper objectMapper;
    private final InMemoryIntradayBarStore barStore;

    public IntradayOhlcConsumer(ObjectMapper objectMapper, InMemoryIntradayBarStore barStore) {
        this.objectMapper = objectMapper;
        this.barStore = barStore;
    }

    @RabbitListener(queues = "market_service_intraday_q")
    public void consumeIntradayUpdate(String message) {
        try {
            Map<String, Object> payload = objectMapper.readValue(
                    message, new TypeReference<Map<String, Object>>() {}
            );

            Object barsObj = payload.get("bars");
            if (!(barsObj instanceof List<?> barsList)) {
                log.debug("Intraday payload has no 'bars' list: {}", payload);
                return;
            }

            int total = 0;
            for (Object symbolEntry : barsList) {
                if (!(symbolEntry instanceof Map<?, ?> symbolMap)) {
                    continue;
                }
                String symbol = stringValue(symbolMap.get("symbol"));
                if (symbol == null || symbol.isBlank()) {
                    log.warn("Intraday bar entry missing 'symbol': {}", symbolMap);
                    continue;
                }
                Object recordsObj = symbolMap.get("records");
                if (!(recordsObj instanceof List<?> recordsList)) {
                    continue;
                }
                for (Object record : recordsList) {
                    if (record instanceof Map<?, ?> rec) {
                        if (upsertBar(symbol, rec)) {
                            total++;
                        }
                    }
                }
            }

            if (total > 0) {
                log.debug("Ingested {} intraday bars across {} symbols", total, barsList.size());
            }
        } catch (Exception ex) {
            log.warn("Failed to process intraday update: {}", ex.getMessage(), ex);
        }
    }

    private boolean upsertBar(String symbol, Map<?, ?> rec) {
        try {
            Instant barTime = parseBarTime(rec.get("time"));
            if (barTime == null) {
                return false;
            }
            String interval = stringValue(rec.get("interval"));
            BigDecimal open = decimalValue(rec.get("open"));
            BigDecimal high = decimalValue(rec.get("high"));
            BigDecimal low = decimalValue(rec.get("low"));
            BigDecimal close = decimalValue(rec.get("close"));
            Long volume = longValue(rec.get("volume"));

            IntradayBar bar = new IntradayBar(barTime, open, high, low, close, volume, interval);
            barStore.upsert(symbol, bar);
            return true;
        } catch (Exception ex) {
            log.warn("Failed to upsert intraday bar for {}: {}", symbol, ex.getMessage());
            return false;
        }
    }

    private Instant parseBarTime(Object value) {
        if (value == null) return null;
        String s = String.valueOf(value).trim();
        if (s.isEmpty()) return null;
        try {
            LocalDateTime ldt = LocalDateTime.parse(s, BAR_TIME_FORMATTER);
            return ldt.toInstant(ICT_OFFSET);
        } catch (DateTimeParseException primary) {
            try {
                return Instant.parse(s);
            } catch (DateTimeParseException fallback) {
                log.warn("Cannot parse bar time '{}'", s);
                return null;
            }
        }
    }

    private static String stringValue(Object value) {
        if (value == null) return null;
        String s = String.valueOf(value).trim();
        return s.isEmpty() ? null : s;
    }

    private static BigDecimal decimalValue(Object value) {
        if (value == null) return null;
        try {
            return new BigDecimal(String.valueOf(value));
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private static Long longValue(Object value) {
        if (value == null) return null;
        try {
            String s = String.valueOf(value);
            return s.isEmpty() ? null : Long.valueOf(s);
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
