package com.stockwise.market.adapter.in.web.dto;

import java.time.LocalDate;
import java.util.List;

public record OhlcSeriesResponse(
        String symbol,
        LocalDate startDate,
        LocalDate endDate,
        List<OhlcPointResponse> data
) {
}
