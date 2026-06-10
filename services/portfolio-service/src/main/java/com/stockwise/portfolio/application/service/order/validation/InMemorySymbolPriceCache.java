package com.stockwise.portfolio.application.service.order.validation;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

/**
 * In-memory thread-safe implementation of SymbolPriceCache.
 * Uses a ConcurrentHashMap to hold cached price values and their daily price bands.
 */
@Component
public class InMemorySymbolPriceCache implements SymbolPriceCache {

    private final Map<String, CachedPrice> cache = new ConcurrentHashMap<>();

    /**
     * Stores a new price entry.
     * Automatically computes ±7% floor and ceiling limits based on the HOSE reference price.
     */
    @Override
    public void put(String symbol, BigDecimal price) {
        String normalized = symbol.trim().toUpperCase();
        BigDecimal floor = price.multiply(new BigDecimal("0.93"));
        BigDecimal ceiling = price.multiply(new BigDecimal("1.07"));
        cache.put(normalized, new CachedPrice(normalized, price, floor, ceiling, LocalDateTime.now()));
    }

    /**
     * Looks up the cached price details for a given symbol, ignoring case and whitespace.
     */
    @Override
    public Optional<CachedPrice> get(String symbol) {
        if (symbol == null) {
            return Optional.empty();
        }
        return Optional.ofNullable(cache.get(symbol.trim().toUpperCase()));
    }

    /**
     * Clears all entries in the cache map.
     */
    @Override
    public void clear() {
        cache.clear();
    }
}
