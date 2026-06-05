package com.stockwise.market.adapter.in.web;

import com.stockwise.market.application.port.in.GetFinancialRatioUseCase;
import com.stockwise.market.application.port.in.GetStockPriceUseCase;
import com.stockwise.market.exception.InvalidDateRangeException;
import com.stockwise.market.exception.InvalidSymbolException;
import com.stockwise.market.exception.SymbolNotFoundException;
import com.stockwise.market.security.JwtAuthenticationFilter;
import com.stockwise.market.security.JwtTokenProvider;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = MarketController.class)
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
}
