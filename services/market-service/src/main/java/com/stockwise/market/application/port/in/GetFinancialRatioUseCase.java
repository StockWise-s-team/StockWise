package com.stockwise.market.application.port.in;

import com.stockwise.market.adapter.in.web.dto.FinancialRatioListResponse;

public interface GetFinancialRatioUseCase {
    FinancialRatioListResponse getRatios(String symbol);
}
