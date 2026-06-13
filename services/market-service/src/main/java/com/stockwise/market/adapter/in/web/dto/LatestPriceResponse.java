package com.stockwise.market.adapter.in.web.dto;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;

public record LatestPriceResponse(
        String symbol,
        BigDecimal price,
        BigDecimal open,
        BigDecimal high,
        BigDecimal low,
        BigDecimal close,
        Long volume,
        BigDecimal change,
        BigDecimal changePercent,
        LocalDate tradeDate,
        Instant updatedAt
) {
}
