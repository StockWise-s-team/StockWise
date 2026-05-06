package com.stockwise.market.application.port.in;

import com.stockwise.market.domain.entity.FinancialRatio;

import java.util.List;

public interface GetFinancialRatioUseCase {
    List<FinancialRatio> getRatios(String symbol);
}
