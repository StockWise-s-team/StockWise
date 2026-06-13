package com.stockwise.market.application.service;

import com.stockwise.market.adapter.in.web.dto.FinancialRatioListResponse;
import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.adapter.in.web.dto.OhlcSeriesResponse;
import com.stockwise.market.domain.entity.FinancialRatio;
import com.stockwise.market.domain.entity.StockPrice;
import com.stockwise.market.domain.repository.FinancialRatioRepository;
import com.stockwise.market.domain.repository.StockPriceRepository;
import com.stockwise.market.exception.InvalidDateRangeException;
import com.stockwise.market.exception.InvalidSymbolException;
import com.stockwise.market.exception.SymbolNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MarketServiceTest {

    @Mock
    private StockPriceRepository stockPriceRepository;

    @Mock
    private FinancialRatioRepository financialRatioRepository;

    @InjectMocks
    private MarketService marketService;

    private StockPrice createStockPrice(String symbol, LocalDate date, BigDecimal close, BigDecimal open,
                                       BigDecimal high, BigDecimal low, Long volume) {
        StockPrice price = new StockPrice();
        price.setId(1L);
        price.setSymbol(symbol);
        price.setTradeDate(date);
        price.setClose(close);
        price.setOpen(open);
        price.setHigh(high);
        price.setLow(low);
        price.setVolume(volume);
        return price;
    }

    @Nested
    @DisplayName("getLatestPrice")
    class GetLatestPriceTests {

        @Test
        @DisplayName("should return latest price with change when two records exist")
        void returnsLatestPriceWithChange() {
            StockPrice older = createStockPrice(
                    "FPT", LocalDate.of(2026, 6, 3),
                    new BigDecimal("115000"), new BigDecimal("114000"),
                    new BigDecimal("116000"), new BigDecimal("113500"),
                    1500000L
            );
            StockPrice latest = createStockPrice(
                    "FPT", LocalDate.of(2026, 6, 4),
                    new BigDecimal("118000"), new BigDecimal("115000"),
                    new BigDecimal("119000"), new BigDecimal("114800"),
                    1800000L
            );
            when(stockPriceRepository.findTop2BySymbolOrderByTradeDateDesc("FPT"))
                    .thenReturn(List.of(latest, older));

            LatestPriceResponse response = marketService.getLatestPrice("FPT");

            assertEquals("FPT", response.symbol());
            assertEquals(new BigDecimal("118000"), response.price());
            assertEquals(new BigDecimal("3000"), response.change());
            assertEquals(new BigDecimal("2.61"), response.changePercent());
            assertEquals(LocalDate.of(2026, 6, 4), response.tradeDate());
            assertEquals(1800000L, response.volume());
        }

        @Test
        @DisplayName("should return zero change when only one record exists")
        void returnsZeroChangeWhenOnlyOneRecord() {
            StockPrice only = createStockPrice(
                    "FPT", LocalDate.of(2026, 6, 4),
                    new BigDecimal("118000"), new BigDecimal("115000"),
                    new BigDecimal("119000"), new BigDecimal("114800"),
                    1800000L
            );
            when(stockPriceRepository.findTop2BySymbolOrderByTradeDateDesc("FPT"))
                    .thenReturn(List.of(only));

            LatestPriceResponse response = marketService.getLatestPrice("FPT");

            assertEquals(BigDecimal.ZERO, response.change());
            assertEquals(BigDecimal.ZERO, response.changePercent());
        }

        @Test
        @DisplayName("should throw SymbolNotFoundException when no data exists")
        void throwsSymbolNotFoundWhenEmpty() {
            when(stockPriceRepository.findTop2BySymbolOrderByTradeDateDesc("XXX"))
                    .thenReturn(Collections.emptyList());

            SymbolNotFoundException ex = assertThrows(
                    SymbolNotFoundException.class,
                    () -> marketService.getLatestPrice("XXX")
            );
            assertTrue(ex.getMessage().contains("XXX"));
        }

        @Test
        @DisplayName("should normalize symbol to uppercase")
        void normalizesSymbolToUppercase() {
            StockPrice only = createStockPrice(
                    "FPT", LocalDate.of(2026, 6, 4),
                    new BigDecimal("118000"), new BigDecimal("115000"),
                    new BigDecimal("119000"), new BigDecimal("114800"),
                    1800000L
            );
            when(stockPriceRepository.findTop2BySymbolOrderByTradeDateDesc("FPT"))
                    .thenReturn(List.of(only));

            LatestPriceResponse response = marketService.getLatestPrice("fpt");

            assertEquals("FPT", response.symbol());
            verify(stockPriceRepository).findTop2BySymbolOrderByTradeDateDesc("FPT");
        }

        @Test
        @DisplayName("should throw InvalidSymbolException for blank symbol")
        void throwsInvalidSymbolForBlank() {
            assertThrows(InvalidSymbolException.class,
                    () -> marketService.getLatestPrice("   "));
        }

        @Test
        @DisplayName("should throw InvalidSymbolException for null symbol")
        void throwsInvalidSymbolForNull() {
            assertThrows(InvalidSymbolException.class,
                    () -> marketService.getLatestPrice(null));
        }
    }

    @Nested
    @DisplayName("getOhlc")
    class GetOhlcTests {

        @Test
        @DisplayName("should return OHLC series sorted by date ascending")
        void returnsOhlcSortedAscending() {
            StockPrice bar1 = createStockPrice(
                    "FPT", LocalDate.of(2026, 6, 1),
                    new BigDecimal("115000"), new BigDecimal("114000"),
                    new BigDecimal("116000"), new BigDecimal("113500"),
                    1500000L
            );
            StockPrice bar2 = createStockPrice(
                    "FPT", LocalDate.of(2026, 6, 2),
                    new BigDecimal("116500"), new BigDecimal("115000"),
                    new BigDecimal("117000"), new BigDecimal("114500"),
                    1600000L
            );
            when(stockPriceRepository.findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(
                    "FPT", LocalDate.of(2026, 6, 1), LocalDate.of(2026, 6, 5)
            )).thenReturn(List.of(bar1, bar2));

            OhlcSeriesResponse response = marketService.getOhlc("FPT", "2026-06-01", "2026-06-05");

            assertEquals("FPT", response.symbol());
            assertEquals(2, response.data().size());
            assertEquals(LocalDate.of(2026, 6, 1), response.data().get(0).date());
            assertEquals(LocalDate.of(2026, 6, 2), response.data().get(1).date());
        }

        @Test
        @DisplayName("should return empty list when no data in range")
        void returnsEmptyListWhenNoData() {
            when(stockPriceRepository.findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(
                    "FPT", LocalDate.of(2026, 6, 1), LocalDate.of(2026, 6, 5)
            )).thenReturn(Collections.emptyList());

            OhlcSeriesResponse response = marketService.getOhlc("FPT", "2026-06-01", "2026-06-05");

            assertTrue(response.data().isEmpty());
        }

        @Test
        @DisplayName("should throw InvalidDateRangeException when startDate is after endDate")
        void throwsInvalidDateRangeWhenStartAfterEnd() {
            assertThrows(InvalidDateRangeException.class,
                    () -> marketService.getOhlc("FPT", "2026-06-10", "2026-06-01"));
        }

        @Test
        @DisplayName("should throw InvalidDateRangeException for invalid date format")
        void throwsInvalidDateRangeForBadFormat() {
            assertThrows(InvalidDateRangeException.class,
                    () -> marketService.getOhlc("FPT", "not-a-date", "2026-06-05"));
        }
    }

    @Nested
    @DisplayName("getRatios")
    class GetRatiosTests {

        @Test
        @DisplayName("should return ratios list for symbol")
        void returnsRatiosList() {
            FinancialRatio ratio = new FinancialRatio();
            ratio.setId(1L);
            ratio.setSymbol("FPT");
            ratio.setPeriod("Q4 2025");
            ratio.setPeRatio(new BigDecimal("25.50"));
            ratio.setPbRatio(new BigDecimal("3.20"));
            ratio.setEps(new BigDecimal("4.05"));
            ratio.setRoe(new BigDecimal("0.18"));
            ratio.setRoa(new BigDecimal("0.09"));

            when(financialRatioRepository.findBySymbolOrderByPeriodDesc("FPT"))
                    .thenReturn(List.of(ratio));

            FinancialRatioListResponse response = marketService.getRatios("FPT");

            assertEquals("FPT", response.symbol());
            assertEquals(1, response.ratios().size());
            assertEquals("Q4 2025", response.ratios().get(0).period());
            assertEquals(new BigDecimal("25.50"), response.ratios().get(0).peRatio());
        }

        @Test
        @DisplayName("should throw SymbolNotFoundException when no ratios exist")
        void throwsSymbolNotFoundWhenEmpty() {
            when(financialRatioRepository.findBySymbolOrderByPeriodDesc("XXX"))
                    .thenReturn(Collections.emptyList());

            SymbolNotFoundException ex = assertThrows(
                    SymbolNotFoundException.class,
                    () -> marketService.getRatios("XXX")
            );
            assertTrue(ex.getMessage().contains("XXX"));
        }
    }
}
