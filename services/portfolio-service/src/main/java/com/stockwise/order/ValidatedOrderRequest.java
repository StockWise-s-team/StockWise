package com.stockwise.order;

import java.math.BigDecimal;
import java.util.UUID;

public record ValidatedOrderRequest(
        UUID userId,
        String symbol,
        String type,
        int quantity,
        BigDecimal price
) {
}
