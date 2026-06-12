package com.stockwise.market.application.service;

import com.stockwise.market.adapter.in.web.dto.FinancialRatioListResponse;
import com.stockwise.market.adapter.in.web.dto.FinancialRatioResponse;
import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.adapter.in.web.dto.OhlcPointResponse;
import com.stockwise.market.adapter.in.web.dto.OhlcSeriesResponse;
import com.stockwise.market.application.port.in.GetFinancialRatioUseCase;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.domain.entity.FinancialRatio;
import com.stockwise.market.domain.entity.StockPrice;
import com.stockwise.market.domain.repository.FinancialRatioRepository;
import com.stockwise.market.domain.repository.StockPriceRepository;
import com.stockwise.market.exception.InvalidDateRangeException;
import com.stockwise.market.exception.InvalidSymbolException;
import com.stockwise.market.exception.SymbolNotFoundException;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.List;

@Service
public class MarketService implements GetStockPriceUseCase, GetFinancialRatioUseCase {

    private final StockPriceRepository stockPriceRepository;
    private final FinancialRatioRepository financialRatioRepository;

    public MarketService(StockPriceRepository stockPriceRepository,
                         FinancialRatioRepository financialRatioRepository) {
        this.stockPriceRepository = stockPriceRepository;
        this.financialRatioRepository = financialRatioRepository;
    }

    @Override
    public LatestPriceResponse getLatestPrice(String symbol) {
        String normalizedSymbol = normalizeSymbol(symbol);
        List<StockPrice> latestPrices = stockPriceRepository.findTop2BySymbolOrderByTradeDateDesc(normalizedSymbol);

        if (latestPrices.isEmpty()) {
            throw new SymbolNotFoundException("No market data found for symbol " + normalizedSymbol);
        }

        StockPrice latest = latestPrices.getFirst();
        StockPrice previous = latestPrices.size() > 1 ? latestPrices.get(1) : null;

        BigDecimal change = BigDecimal.ZERO;
        BigDecimal changePercent = BigDecimal.ZERO;

        if (previous != null && previous.getClose() != null && latest.getClose() != null
                && previous.getClose().compareTo(BigDecimal.ZERO) != 0) {
            change = latest.getClose().subtract(previous.getClose());
            changePercent = change
                    .divide(previous.getClose(), 4, RoundingMode.HALF_UP)
                    .multiply(BigDecimal.valueOf(100))
                    .setScale(2, RoundingMode.HALF_UP);
        }

        return new LatestPriceResponse(
                latest.getSymbol(),
                latest.getClose(),
                latest.getOpen(),
                latest.getHigh(),
                latest.getLow(),
                latest.getClose(),
                latest.getVolume(),
                change,
                changePercent,
                latest.getTradeDate(),
                toUpdatedAt(latest.getTradeDate())
        );
    }

    @Override
    public OhlcSeriesResponse getOhlc(String symbol, String startDate, String endDate) {
        String normalizedSymbol = normalizeSymbol(symbol);
        LocalDate start = parseDate(startDate, "startDate");
        LocalDate end = parseDate(endDate, "endDate");

        if (start.isAfter(end)) {
            throw new InvalidDateRangeException("startDate must be before or equal to endDate");
        }

        List<StockPrice> prices = stockPriceRepository
                .findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(normalizedSymbol, start, end);

        List<OhlcPointResponse> data = prices.stream()
                .map(this::toOhlcPointResponse)
                .toList();

        return new OhlcSeriesResponse(normalizedSymbol, start, end, data);
    }

    @Override
    public FinancialRatioListResponse getRatios(String symbol) {
        String normalizedSymbol = normalizeSymbol(symbol);
        List<FinancialRatio> ratios = financialRatioRepository.findBySymbolOrderByPeriodDesc(normalizedSymbol);

        if (ratios.isEmpty()) {
            throw new SymbolNotFoundException("No financial ratios found for symbol " + normalizedSymbol);
        }

        List<FinancialRatioResponse> responses = ratios.stream()
                .map(this::toFinancialRatioResponse)
                .toList();

        return new FinancialRatioListResponse(normalizedSymbol, responses);
    }

    private String normalizeSymbol(String symbol) {
        if (symbol == null) {
            throw new InvalidSymbolException("symbol is required");
        }

        String normalized = symbol.trim().toUpperCase();
        if (normalized.isBlank()) {
            throw new InvalidSymbolException("symbol must not be blank");
        }

        if (normalized.length() > 10 || !normalized.matches("^[A-Z0-9._-]+$")) {
            throw new InvalidSymbolException("symbol contains invalid characters");
        }

        return normalized;
    }

    private LocalDate parseDate(String rawDate, String fieldName) {
        try {
            return LocalDate.parse(rawDate);
        } catch (DateTimeParseException ex) {
            throw new InvalidDateRangeException(fieldName + " must be a valid ISO date (yyyy-MM-dd)");
        }
    }

    private Instant toUpdatedAt(LocalDate tradeDate) {
        return tradeDate.atStartOfDay(java.time.ZoneOffset.UTC).toInstant();
    }

    private OhlcPointResponse toOhlcPointResponse(StockPrice price) {
        return new OhlcPointResponse(
                price.getTradeDate(),
                price.getOpen(),
                price.getHigh(),
                price.getLow(),
                price.getClose(),
                price.getVolume()
        );
    }

    private FinancialRatioResponse toFinancialRatioResponse(FinancialRatio ratio) {
        return new FinancialRatioResponse(
                ratio.getPeriod(),
                ratio.getPeRatio(),
                ratio.getPbRatio(),
                ratio.getEps(),
                ratio.getRoe(),
                ratio.getRoa()
        );
    }
}
