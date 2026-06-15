package com.stockwise.market.adapter.in.web;

import com.stockwise.market.adapter.in.web.dto.FinancialRatioListResponse;
import com.stockwise.market.adapter.in.web.dto.IntradayPriceDto;
import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.adapter.in.web.dto.OhlcSeriesResponse;
import com.stockwise.market.application.port.in.GetFinancialRatioUseCase;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.domain.repository.IntradayPriceRepository;
import com.stockwise.market.messaging.MarketDataConsumer;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.messaging.MarketDataConsumer;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/market")
public class MarketController {

    private final GetStockPriceUseCase getStockPriceUseCase;
    private final GetFinancialRatioUseCase getFinancialRatioUseCase;
    private final MarketDataConsumer marketDataConsumer;
    private final IntradayPriceRepository intradayPriceRepository;

    public MarketController(GetStockPriceUseCase getStockPriceUseCase,
                           GetFinancialRatioUseCase getFinancialRatioUseCase,
                           MarketDataConsumer marketDataConsumer,
                           IntradayPriceRepository intradayPriceRepository) {
        this.getStockPriceUseCase = getStockPriceUseCase;
        this.getFinancialRatioUseCase = getFinancialRatioUseCase;
        this.marketDataConsumer = marketDataConsumer;
        this.intradayPriceRepository = intradayPriceRepository;
    }

    @GetMapping("/price/{symbol}")
    public ResponseEntity<LatestPriceResponse> getPrice(@PathVariable String symbol) {
        LatestPriceResponse cached = marketDataConsumer.getCachedPrice(symbol);
        if (cached != null) {
            return ResponseEntity.ok(cached);
        }
        return ResponseEntity.ok(getStockPriceUseCase.getLatestPrice(symbol));
    }

    @GetMapping("/price/batch")
    public ResponseEntity<Map<String, LatestPriceResponse>> getPriceBatch(
            @RequestParam("symbols") List<String> symbols) {
        Map<String, LatestPriceResponse> cached = marketDataConsumer.getCachedPrices(symbols);

        Map<String, LatestPriceResponse> out = new LinkedHashMap<>();
        for (String sym : symbols) {
            if (sym == null || sym.isBlank()) continue;
            String normalized = sym.trim().toUpperCase();
            LatestPriceResponse price = cached.get(normalized);
            if (price == null) {
                try {
                    price = getStockPriceUseCase.getLatestPrice(normalized);
                } catch (Exception ex) {
                    log.debug("Skipping symbol {} in batch response: {}", normalized, ex.getMessage());
                    continue;
                }
            }
            out.put(normalized, price);
        }
        return ResponseEntity.ok(out);
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

    @GetMapping("/prices/intraday/{symbol}")
    public ResponseEntity<List<IntradayPriceDto>> getIntradayPrices(@PathVariable String symbol) {
        Instant oneHourAgo = Instant.now().minus(1, ChronoUnit.HOURS);
        List<IntradayPriceDto> result = intradayPriceRepository
                .findBySymbolAndTimestampAfterOrderByTimestampAsc(symbol.trim().toUpperCase(), oneHourAgo)
                .stream()
                .map(p -> new IntradayPriceDto(p.getSymbol(), p.getPrice(), p.getTimestamp()))
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }

    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(MarketController.class);
}
