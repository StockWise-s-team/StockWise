package com.stockwise.portfolio.application.port.in;

import com.stockwise.portfolio.domain.entity.Order;

import java.math.BigDecimal;
import java.util.UUID;

public interface PlaceOrderUseCase {
    Order placeOrder(UUID userId, String symbol, String type, Integer quantity);

    Order placeOrder(UUID userId, String symbol, String type, Integer quantity, BigDecimal price);
}
