package com.stockwise.portfolio.adapter.in.web.dto;

import com.stockwise.portfolio.domain.entity.Order;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

public record OrderHistoryResponse(
        UUID id,
        String symbol,
        String type,
        BigDecimal price,
        Integer quantity,
        String status,
        LocalDateTime createdAt,
        LocalDateTime cancelledAt
) {
    public static OrderHistoryResponse from(Order order) {
        return new OrderHistoryResponse(
                order.getId(),
                order.getSymbol(),
                order.getType(),
                order.getPrice(),
                order.getQuantity(),
                order.getStatus(),
                order.getCreatedAt(),
                order.getCancelledAt()
        );
    }
}
