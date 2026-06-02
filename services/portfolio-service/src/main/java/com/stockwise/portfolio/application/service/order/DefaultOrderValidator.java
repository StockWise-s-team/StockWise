package com.stockwise.portfolio.application.service.order;

import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.UUID;

@Component
public class DefaultOrderValidator implements OrderValidator {

    @Override
    public ValidatedOrderRequest validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price) {
        return new ValidatedOrderRequest(
                validateUserId(userId),
                validateSymbol(symbol),
                validateType(type),
                validateQuantity(quantity),
                validatePrice(price)
        );
    }

    private UUID validateUserId(UUID userId) {
        if (userId == null) {
            throw new BadRequestException("userId is required");
        }
        return userId;
    }

    private String validateSymbol(String symbol) {
        if (symbol == null || symbol.isBlank()) {
            throw new BadRequestException("symbol is required");
        }
        String normalized = symbol.trim().toUpperCase();
        if (!normalized.matches("[A-Z0-9.]{1,10}")) {
            throw new BadRequestException("symbol must be 1-10 uppercase letters, digits, or dots");
        }
        return normalized;
    }

    private String validateType(String type) {
        if (type == null || type.isBlank()) {
            throw new BadRequestException("type is required");
        }
        String normalized = type.trim().toUpperCase();
        if (!normalized.matches("[A-Z]{1,20}")) {
            throw new BadRequestException("type must contain uppercase letters only");
        }
        return normalized;
    }

    private int validateQuantity(Integer quantity) {
        if (quantity == null || quantity <= 0) {
            throw new BadRequestException("quantity must be greater than zero");
        }
        return quantity;
    }

    private BigDecimal validatePrice(BigDecimal price) {
        BigDecimal effectivePrice = price == null ? OrderConstants.DEFAULT_ORDER_PRICE : price;
        if (effectivePrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BadRequestException("price must be greater than zero");
        }
        return effectivePrice.setScale(2, RoundingMode.HALF_UP);
    }
}
