package com.stockwise.market.adapter.in.web;

import com.stockwise.market.adapter.in.web.dto.FinancialRatioListResponse;
import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.adapter.in.web.dto.OhlcSeriesResponse;
import com.stockwise.market.application.port.in.GetFinancialRatioUseCase;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.messaging.MarketDataConsumer;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/market")
@RequiredArgsConstructor
public class MarketController {

    private final GetStockPriceUseCase getStockPriceUseCase;
    private final GetFinancialRatioUseCase getFinancialRatioUseCase;
    private final MarketDataConsumer marketDataConsumer;

    @GetMapping("/price/{symbol}")
    public ResponseEntity<LatestPriceResponse> getPrice(@PathVariable String symbol) {
        LatestPriceResponse cached = marketDataConsumer.getCachedPrice(symbol);
        if (cached != null) {
            return ResponseEntity.ok(cached);
        }
        return ResponseEntity.ok(getStockPriceUseCase.getLatestPrice(symbol));
    }

    @GetMapping("/ratio/{symbol}")
    public ResponseEntity<FinancialRatioListResponse> getRatio(@PathVariable String symbol) {
        return ResponseEntity.ok(getFinancialRatioUseCase.getRatios(symbol));
    }

    @GetMapping("/ohlc/{symbol}")
    public ResponseEntity<OhlcSeriesResponse> getOhlc(
            @PathVariable String symbol,
            @RequestParam(defaultValue = "2024-01-01") String startDate,
            @RequestParam(defaultValue = "2025-12-31") String endDate) {
        return ResponseEntity.ok(getStockPriceUseCase.getOhlc(symbol, startDate, endDate));
    }
}
