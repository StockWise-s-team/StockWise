package com.stockwise.portfolio.application.service.order.validation;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

/**
 * Interface representing a cache for storing current stock prices.
 * Used to decouple the order validation/matching engine from low-level cache storage details (DIP).
 */
public interface SymbolPriceCache {

    /**
     * Record representing a cached stock price with calculated floor/ceiling bands.
     */
    record CachedPrice(
            String symbol,
            BigDecimal price,
            BigDecimal floorPrice,
            BigDecimal ceilingPrice,
            LocalDateTime updatedAt
    ) {}

    /**
     * Caches a new stock price.
     * Calculates the daily price floor and ceiling bands from HOSE standard limits.
     *
     * @param symbol the ticker symbol of the stock
     * @param price  the latest market price
     */
    void put(String symbol, BigDecimal price);

    /**
     * Retrieves the cached price details for a given stock symbol.
     *
     * @param symbol the ticker symbol
     * @return an Optional containing the CachedPrice, or empty if not cached
     */
    Optional<CachedPrice> get(String symbol);

    /**
     * Clears all cached price entries.
     */
    void clear();
}
