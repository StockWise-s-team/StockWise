package com.stockwise.market.adapter.in.web.dto;

import java.math.BigDecimal;
import java.time.Instant;

public record IntradayOhlcBarResponse(
        Instant time,
        BigDecimal open,
        BigDecimal high,
        BigDecimal low,
        BigDecimal close,
        Long volume,
        String interval
) {
}
