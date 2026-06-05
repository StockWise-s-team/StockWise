package com.stockwise.market.adapter.in.web.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public record OhlcPointResponse(
        LocalDate date,
        BigDecimal open,
        BigDecimal high,
        BigDecimal low,
        BigDecimal close,
        Long volume
) {
}
