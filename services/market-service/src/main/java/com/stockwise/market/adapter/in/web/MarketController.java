package com.stockwise.market.adapter.in.web;

import com.stockwise.market.application.port.in.GetFinancialRatioUseCase;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.domain.entity.FinancialRatio;
import com.stockwise.market.domain.entity.StockPrice;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/market")
@RequiredArgsConstructor
public class MarketController {

    private final GetStockPriceUseCase getStockPriceUseCase;
    private final GetFinancialRatioUseCase getFinancialRatioUseCase;

    @GetMapping("/price/{symbol}")
    public ResponseEntity<StockPrice> getPrice(@PathVariable String symbol) {
        return ResponseEntity.ok(getStockPriceUseCase.getLatestPrice(symbol));
    }

    @GetMapping("/ratio/{symbol}")
    public ResponseEntity<List<FinancialRatio>> getRatio(@PathVariable String symbol) {
        return ResponseEntity.ok(getFinancialRatioUseCase.getRatios(symbol));
    }

    @GetMapping("/ohlc/{symbol}")
    public ResponseEntity<List<StockPrice>> getOhlc(
            @PathVariable String symbol,
            @RequestParam(defaultValue = "2024-01-01") String startDate,
            @RequestParam(defaultValue = "2025-12-31") String endDate) {
        return ResponseEntity.ok(getStockPriceUseCase.getOhlc(symbol, startDate, endDate));
    }
}
