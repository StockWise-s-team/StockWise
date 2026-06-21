package com.stockwise.market.application.store;

import java.math.BigDecimal;
import java.time.Instant;

public record IntradayBar(
        Instant barTime,
        BigDecimal open,
        BigDecimal high,
        BigDecimal low,
        BigDecimal close,
        Long volume,
        String interval
) {
}
