package com.stockwise.market.adapter.in.web.dto;

import java.math.BigDecimal;

public record FinancialRatioResponse(
        String period,
        BigDecimal peRatio,
        BigDecimal pbRatio,
        BigDecimal eps,
        BigDecimal roe,
        BigDecimal roa
) {
}
