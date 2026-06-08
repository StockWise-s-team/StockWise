package com.stockwise.market.adapter.in.web.dto;

import java.util.List;

public record FinancialRatioListResponse(
        String symbol,
        List<FinancialRatioResponse> ratios
) {
}
