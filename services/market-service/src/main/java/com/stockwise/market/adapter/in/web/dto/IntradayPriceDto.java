package com.stockwise.market.adapter.in.web.dto;

import java.math.BigDecimal;
import java.time.Instant;

public record IntradayPriceDto(
        String symbol,
        BigDecimal price,
        Instant timestamp
) {
}
