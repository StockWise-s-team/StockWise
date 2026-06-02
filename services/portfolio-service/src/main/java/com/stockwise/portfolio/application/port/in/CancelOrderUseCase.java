package com.stockwise.portfolio.application.port.in;

import com.stockwise.portfolio.domain.entity.Order;

import java.util.Optional;
import java.util.UUID;

public interface CancelOrderUseCase {
    Order cancelOrder(UUID orderId, Optional<UUID> userId);
}
