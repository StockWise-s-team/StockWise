package com.stockwise.market.application.port.in;

import com.stockwise.market.domain.entity.StockPrice;

import java.util.List;

public interface GetStockPriceUseCase {
    StockPrice getLatestPrice(String symbol);
    List<StockPrice> getOhlc(String symbol, String startDate, String endDate);
}
