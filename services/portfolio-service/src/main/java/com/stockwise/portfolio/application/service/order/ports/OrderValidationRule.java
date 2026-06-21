package com.stockwise.portfolio.application.service.order.ports;

import java.math.BigDecimal;
import java.util.UUID;

/**
 * Interface representing a single order validation rule.
 * Implementing classes define specific validation criteria (e.g. format, trading hours, price limits).
 * This supports the Open/Closed Principle (OCP) as new rules can be added without changing the validator.
 */
public interface OrderValidationRule {
    
    /**
     * Validates the details of an order request.
     * Throws a BadRequestException if validation fails.
     *
     * @param userId   the ID of the user placing the order
     * @param symbol   the ticker symbol of the stock
     * @param type     the side of the order (BUY/SELL)
     * @param quantity the number of shares
     * @param price    the limit price, or null if it's a market order
     */
    void validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price);
}
