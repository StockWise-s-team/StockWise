package com.stockwise.portfolio.application.service.order.validation;

import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.application.service.order.ValidatedOrderRequest;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.UUID;

/**
 * Default implementation of the OrderValidator port interface.
 * Implements the chain of validation rules pattern to ensure single responsibility (SRP)
 * and ease of extensibility (OCP).
 */
@Component
public class DefaultOrderValidator implements OrderValidator {

    private final List<OrderValidationRule> validationRules;
    private final SymbolPriceCache symbolPriceCache;
    private final com.stockwise.portfolio.domain.repository.OrderRepository orderRepository;

    public DefaultOrderValidator(
            List<OrderValidationRule> validationRules,
            SymbolPriceCache symbolPriceCache,
            com.stockwise.portfolio.domain.repository.OrderRepository orderRepository) {
        this.validationRules = validationRules;
        this.symbolPriceCache = symbolPriceCache;
        this.orderRepository = orderRepository;
    }

    /**
     * Executes the validation rule chain and returns a validated order request record.
     * Maps null limit prices to current cached market prices.
     */
    @Override
    public ValidatedOrderRequest validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price) {
        // Execute all validation rules in sequence (SRP & OCP compliant)
        for (OrderValidationRule rule : validationRules) {
            rule.validate(userId, symbol, type, quantity, price);
        }

        String validSymbol = symbol.trim().toUpperCase();
        String validType = type.trim().toUpperCase();
        int validQuantity = quantity;

        BigDecimal effectivePrice;
        if (price == null) {
            BigDecimal cachedPrice = symbolPriceCache.get(validSymbol)
                    .map(SymbolPriceCache.CachedPrice::price)
                    .orElse(null);
            if (cachedPrice != null) {
                effectivePrice = cachedPrice;
            } else {
                BigDecimal dbPrice = orderRepository.findLatestPriceBySymbol(validSymbol);
                effectivePrice = dbPrice != null ? dbPrice : OrderConstants.DEFAULT_ORDER_PRICE;
            }
        } else {
            effectivePrice = price;
        }

        return new ValidatedOrderRequest(
                userId,
                validSymbol,
                validType,
                validQuantity,
                effectivePrice.setScale(2, RoundingMode.HALF_UP)
        );
    }
}
