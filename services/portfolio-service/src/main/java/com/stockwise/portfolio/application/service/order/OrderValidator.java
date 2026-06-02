package com.stockwise.portfolio.application.service.order;

import java.math.BigDecimal;
import java.util.UUID;

public interface OrderValidator {
    ValidatedOrderRequest validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price);
}
