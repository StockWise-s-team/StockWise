package com.stockwise.market.application.service;

import com.stockwise.market.adapter.in.web.dto.IntradayOhlcBarResponse;
import com.stockwise.market.adapter.in.web.dto.IntradayOhlcResponse;
import com.stockwise.market.application.store.InMemoryIntradayBarStore;
import com.stockwise.market.application.store.IntradayBar;
import com.stockwise.market.exception.InvalidSymbolException;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Service
public class IntradayOhlcService {

    private static final String DEFAULT_INTERVAL = "5m";

    private final InMemoryIntradayBarStore barStore;

    public IntradayOhlcService(InMemoryIntradayBarStore barStore) {
        this.barStore = barStore;
    }

    public IntradayOhlcResponse getIntradayBars(String symbol, String interval) {
        String normalized = normalizeSymbol(symbol);
        String targetInterval = (interval == null || interval.isBlank()) ? DEFAULT_INTERVAL : interval;
        List<IntradayBar> bars = barStore.getBars(normalized, targetInterval);
        List<IntradayOhlcBarResponse> data = new ArrayList<>(bars.size());
        for (IntradayBar b : bars) {
            data.add(new IntradayOhlcBarResponse(
                    b.barTime(),
                    b.open(),
                    b.high(),
                    b.low(),
                    b.close(),
                    b.volume(),
                    b.interval()
            ));
        }
        return new IntradayOhlcResponse(normalized, targetInterval, data, Instant.now());
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
}
