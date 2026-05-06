package com.stockwise.market.application.service;

import com.stockwise.market.application.port.in.GetFinancialRatioUseCase;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.domain.entity.FinancialRatio;
import com.stockwise.market.domain.entity.StockPrice;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Service
public class MarketService implements GetStockPriceUseCase, GetFinancialRatioUseCase {

    @Override
    public StockPrice getLatestPrice(String symbol) {
        StockPrice price = new StockPrice();
        price.setId(1L);
        price.setSymbol(symbol);
        price.setTradeDate(LocalDate.now());
        price.setOpen(new BigDecimal("100.00"));
        price.setHigh(new BigDecimal("105.00"));
        price.setLow(new BigDecimal("99.00"));
        price.setClose(new BigDecimal("103.50"));
        price.setVolume(1000000L);
        return price;
    }

    @Override
    public List<StockPrice> getOhlc(String symbol, String startDate, String endDate) {
        return List.of(getLatestPrice(symbol));
    }

    @Override
    public List<FinancialRatio> getRatios(String symbol) {
        FinancialRatio ratio = new FinancialRatio();
        ratio.setId(1L);
        ratio.setSymbol(symbol);
        ratio.setPeriod("Q4 2025");
        ratio.setPeRatio(new BigDecimal("25.50"));
        ratio.setPbRatio(new BigDecimal("3.20"));
        ratio.setEps(new BigDecimal("4.05"));
        ratio.setRoe(new BigDecimal("0.18"));
        ratio.setRoa(new BigDecimal("0.09"));
        return List.of(ratio);
    }
}
