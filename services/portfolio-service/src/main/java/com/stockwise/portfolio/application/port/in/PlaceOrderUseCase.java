package com.stockwise.portfolio.application.port.in;

import com.stockwise.portfolio.domain.entity.Transaction;

import java.util.UUID;

public interface PlaceOrderUseCase {
    Transaction placeOrder(UUID userId, String symbol, String type, Integer quantity);

    Transaction placeOrder(UUID userId, String symbol, String type, Integer quantity, java.math.BigDecimal price);
}
