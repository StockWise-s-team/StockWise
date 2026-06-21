package com.stockwise.portfolio.application.service.order.ports;

import com.stockwise.portfolio.application.service.order.ValidatedOrderRequest;

import java.math.BigDecimal;
import java.util.UUID;

public interface OrderValidator {
    ValidatedOrderRequest validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price);
}
