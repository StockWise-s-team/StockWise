package com.stockwise.market.application.port.in;

import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.adapter.in.web.dto.OhlcSeriesResponse;

public interface GetStockPriceUseCase {
    LatestPriceResponse getLatestPrice(String symbol);

    OhlcSeriesResponse getOhlc(String symbol, String startDate, String endDate);
}
