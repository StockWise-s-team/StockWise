package com.stockwise.portfolio.adapter.in.web.dto;

import java.math.BigDecimal;
import java.util.UUID;

public record PlaceOrderRequest(
        UUID userId,
        String symbol,
        String type,
        Integer quantity,
        BigDecimal price
) {
}
