package com.stockwise.portfolio.application.service.order.validation;

import com.stockwise.portfolio.application.service.order.ports.OrderValidationRule;
import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.UUID;

/**
 * Validation rule to check basic format constraints of an order request.
 * Ensures fields like userId, symbol, type, quantity, and price have valid shapes and values.
 * Runs first in the validation chain.
 */
@Component
@Order(1)
public class BasicFormatValidationRule implements OrderValidationRule {

    /**
     * Validates basic format constraints:
     * - Fields cannot be null or blank
     * - Symbol must match a regular expression alphanumeric format
     * - Quantity and price must be greater than zero
     */
    @Override
    public void validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price) {
        if (userId == null) {
            throw new BadRequestException("userId is required");
        }
        if (symbol == null || symbol.isBlank()) {
            throw new BadRequestException("symbol is required");
        }
        String normalizedSymbol = symbol.trim().toUpperCase();
        if (!normalizedSymbol.matches("[A-Z0-9.]{1,10}")) {
            throw new BadRequestException("symbol must be 1-10 uppercase letters, digits, or dots");
        }
        if (type == null || type.isBlank()) {
            throw new BadRequestException("type is required");
        }
        String normalizedType = type.trim().toUpperCase();
        if (!normalizedType.matches("[A-Z]{1,20}")) {
            throw new BadRequestException("type must contain uppercase letters only");
        }
        if (quantity == null || quantity <= 0) {
            throw new BadRequestException("quantity must be greater than zero");
        }
        if (price != null && price.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BadRequestException("price must be greater than zero");
        }
    }
}
