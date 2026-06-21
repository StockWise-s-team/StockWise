package com.stockwise.market.adapter.in.web;

import com.stockwise.market.adapter.in.web.dto.IntradayOhlcBarResponse;
import com.stockwise.market.adapter.in.web.dto.IntradayOhlcResponse;
import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.application.port.in.GetFinancialRatioUseCase;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.application.service.IntradayOhlcService;
import com.stockwise.market.domain.repository.IntradayPriceRepository;
import com.stockwise.market.exception.InvalidDateRangeException;
import com.stockwise.market.exception.InvalidSymbolException;
import com.stockwise.market.exception.SymbolNotFoundException;
import com.stockwise.market.security.JwtAuthenticationFilter;
import com.stockwise.market.security.JwtTokenProvider;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = MarketController.class)
@AutoConfigureMockMvc(addFilters = false)
@Import(com.stockwise.market.exception.GlobalExceptionHandler.class)
class MarketControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private GetStockPriceUseCase getStockPriceUseCase;

    @MockBean
    private GetFinancialRatioUseCase getFinancialRatioUseCase;

    @MockBean
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @MockBean
    private JwtTokenProvider jwtTokenProvider;

    @MockBean
    private com.stockwise.market.messaging.MarketDataConsumer marketDataConsumer;

    @MockBean
    private IntradayPriceRepository intradayPriceRepository;

    @MockBean
    private IntradayOhlcService intradayOhlcService;

    @Test
    @DisplayName("should return 404 with error response when symbol not found")
    void returns404WhenSymbolNotFound() throws Exception {
        when(getStockPriceUseCase.getLatestPrice("MISSING"))
                .thenThrow(new SymbolNotFoundException("No market data found for symbol MISSING"));

        mockMvc.perform(get("/market/price/MISSING")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error").value("SYMBOL_NOT_FOUND"))
                .andExpect(jsonPath("$.message").value("No market data found for symbol MISSING"));
    }

    @Test
    @DisplayName("should return 400 for invalid symbol")
    void returns400ForInvalidSymbol() throws Exception {
        when(getFinancialRatioUseCase.getRatios("***"))
                .thenThrow(new InvalidSymbolException("symbol contains invalid characters"));

        mockMvc.perform(get("/market/ratio/***")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("INVALID_SYMBOL"));
    }

    @Test
    @DisplayName("should return 400 for invalid date range")
    void returns400ForInvalidDateRange() throws Exception {
        when(getStockPriceUseCase.getOhlc("FPT", "2026-06-10", "2026-06-01"))
                .thenThrow(new InvalidDateRangeException("startDate must be before or equal to endDate"));

        mockMvc.perform(get("/market/ohlc/FPT")
                        .queryParam("startDate", "2026-06-10")
                        .queryParam("endDate", "2026-06-01")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("INVALID_DATE_RANGE"));
    }

    @Test
    @DisplayName("should return cached prices for batch endpoint")
    void returnsCachedBatchPrices() throws Exception {
        LatestPriceResponse fpt = new LatestPriceResponse(
                "FPT", new BigDecimal("120000"), new BigDecimal("118000"),
                new BigDecimal("121000"), new BigDecimal("118000"),
                new BigDecimal("120000"), 1500000L,
                new BigDecimal("2000"), new BigDecimal("1.69"),
                LocalDate.of(2026, 6, 14), java.time.Instant.now()
        );
        when(marketDataConsumer.getCachedPrices(List.of("FPT"))).thenReturn(Map.of("FPT", fpt));

        mockMvc.perform(get("/market/price/batch")
                        .param("symbols", "FPT")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.FPT.symbol").value("FPT"))
                .andExpect(jsonPath("$.FPT.price").value(120000));
    }

    @Test
    @DisplayName("should fall back to use case when cache miss in batch")
    void fallsBackToUseCaseInBatch() throws Exception {
        LatestPriceResponse shb = new LatestPriceResponse(
                "SHB", new BigDecimal("14000"), new BigDecimal("13900"),
                new BigDecimal("14100"), new BigDecimal("13800"),
                new BigDecimal("14000"), 2000000L,
                new BigDecimal("100"), new BigDecimal("0.72"),
                LocalDate.of(2026, 6, 14), java.time.Instant.now()
        );
        when(marketDataConsumer.getCachedPrices(List.of("SHB"))).thenReturn(Map.of());
        when(getStockPriceUseCase.getLatestPrice("SHB")).thenReturn(shb);

        mockMvc.perform(get("/market/price/batch")
                        .param("symbols", "SHB")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.SHB.symbol").value("SHB"))
                .andExpect(jsonPath("$.SHB.close").value(14000));
    }

    @Test
    @DisplayName("should return intraday OHLC bars from service")
    void returnsIntradayOhlcBars() throws Exception {
        Instant bar1 = Instant.now().truncatedTo(ChronoUnit.MINUTES).minus(5, ChronoUnit.MINUTES);
        Instant bar2 = bar1.plus(5, ChronoUnit.MINUTES);
        List<IntradayOhlcBarResponse> bars = List.of(
                new IntradayOhlcBarResponse(bar1, new BigDecimal("100"), new BigDecimal("105"),
                        new BigDecimal("99"), new BigDecimal("103"), 1000L, "5m"),
                new IntradayOhlcBarResponse(bar2, new BigDecimal("103"), new BigDecimal("108"),
                        new BigDecimal("102"), new BigDecimal("107"), 1500L, "5m")
        );
        when(intradayOhlcService.getIntradayBars(eq("FPT"), eq("5m")))
                .thenReturn(new IntradayOhlcResponse("FPT", "5m", bars, Instant.now()));

        mockMvc.perform(get("/market/ohlc/intraday/FPT")
                        .param("interval", "5m")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.symbol").value("FPT"))
                .andExpect(jsonPath("$.interval").value("5m"))
                .andExpect(jsonPath("$.data.length()").value(2))
                .andExpect(jsonPath("$.data[0].open").value(100))
                .andExpect(jsonPath("$.data[0].high").value(105))
                .andExpect(jsonPath("$.data[1].close").value(107));
    }

    @Test
    @DisplayName("should default interval to 5m when not provided")
    void defaultsIntervalTo5m() throws Exception {
        when(intradayOhlcService.getIntradayBars(eq("FPT"), eq("5m")))
                .thenReturn(new IntradayOhlcResponse("FPT", "5m", List.of(), Instant.now()));

        mockMvc.perform(get("/market/ohlc/intraday/FPT")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.interval").value("5m"))
                .andExpect(jsonPath("$.data.length()").value(0));
    }
}
