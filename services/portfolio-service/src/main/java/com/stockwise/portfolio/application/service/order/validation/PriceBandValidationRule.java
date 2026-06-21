package com.stockwise.portfolio.application.service.order.validation;

import com.stockwise.portfolio.application.service.order.ports.OrderValidationRule;
import com.stockwise.portfolio.application.service.order.ports.SymbolPriceCache;
import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Optional;
import java.util.UUID;

/**
 * Validation rule enforcing daily price limit band limits (BR-100).
 * Ensures that the order limit price is within the daily trading band [floor, ceiling]
 * calculated from the base market reference price (e.g. ±7% daily change limits in HOSE standard).
 */
@Component
@Order(3)
public class PriceBandValidationRule implements OrderValidationRule {

    private final SymbolPriceCache symbolPriceCache;
    private final boolean tradingHoursEnabled;

    public PriceBandValidationRule(
            SymbolPriceCache symbolPriceCache,
            @Value("${trading.hours.enabled:true}") boolean tradingHoursEnabled) {
        this.symbolPriceCache = symbolPriceCache;
        this.tradingHoursEnabled = tradingHoursEnabled;
    }

    /**
     * Validates that the order price is within the allowed daily band limits.
     * Uses the local price cache containing reference prices from market data update broadcasts.
     */
    @Override
    public void validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price) {
        String normalizedSymbol = symbol.trim().toUpperCase();
        Optional<SymbolPriceCache.CachedPrice> priceOpt = symbolPriceCache.get(normalizedSymbol);

        if (priceOpt.isEmpty() && tradingHoursEnabled) {
            throw new BadRequestException("Market data not available for symbol: " + normalizedSymbol);
        }

        if (priceOpt.isPresent() && price != null) {
            SymbolPriceCache.CachedPrice symbolPrice = priceOpt.get();
            BigDecimal floor = symbolPrice.floorPrice();
            BigDecimal ceiling = symbolPrice.ceilingPrice();

            if (floor == null) {
                floor = symbolPrice.price().multiply(new BigDecimal("0.93"));
            }
            if (ceiling == null) {
                ceiling = symbolPrice.price().multiply(new BigDecimal("1.07"));
            }

            if (price.compareTo(floor) < 0 || price.compareTo(ceiling) > 0) {
                throw new BadRequestException(String.format(
                        "Order price %s is out of the daily price band [%s, %s] for %s",
                        price.setScale(2, RoundingMode.HALF_UP),
                        floor.setScale(2, RoundingMode.HALF_UP),
                        ceiling.setScale(2, RoundingMode.HALF_UP),
                        normalizedSymbol
                ));
            }
        }
    }
}
