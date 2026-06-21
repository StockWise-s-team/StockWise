package com.stockwise.market.application.service;

import com.stockwise.market.application.store.InMemoryIntradayBarStore;
import com.stockwise.market.application.store.IntradayBar;
import com.stockwise.market.exception.InvalidSymbolException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class IntradayOhlcServiceTest {

    private InMemoryIntradayBarStore store;
    private IntradayOhlcService service;

    @BeforeEach
    void setUp() {
        store = new InMemoryIntradayBarStore();
        service = new IntradayOhlcService(store);
    }

    @Test
    @DisplayName("getIntradayBars normalizes symbol and returns stored bars")
    void returnsStoredBars() {
        Instant t1 = Instant.parse("2026-06-16T02:15:00Z");
        Instant t2 = Instant.parse("2026-06-16T02:20:00Z");
        store.upsert("VHM", new IntradayBar(t1, bd("100"), bd("110"), bd("95"), bd("105"), 1000L, "5m"));
        store.upsert("VHM", new IntradayBar(t2, bd("105"), bd("115"), bd("100"), bd("112"), 800L, "5m"));

        var response = service.getIntradayBars(" vhm ", "5m");

        assertEquals("VHM", response.symbol());
        assertEquals("5m", response.interval());
        assertEquals(2, response.data().size());
        assertEquals(t1, response.data().get(0).time());
        assertEquals(0, bd("112").compareTo(response.data().get(1).close()));
    }

    @Test
    @DisplayName("getIntradayBars defaults interval to 5m when blank")
    void defaultsIntervalTo5m() {
        store.upsert("VHM", new IntradayBar(Instant.parse("2026-06-16T02:15:00Z"),
                bd("100"), bd("110"), bd("95"), bd("105"), 1L, "5m"));

        var response = service.getIntradayBars("VHM", "");

        assertEquals("5m", response.interval());
        assertEquals(1, response.data().size());
    }

    @Test
    @DisplayName("getIntradayBars returns empty list when no bars for symbol")
    void returnsEmptyForUnknownSymbol() {
        var response = service.getIntradayBars("ZZZ", "5m");

        assertEquals("ZZZ", response.symbol());
        assertEquals(0, response.data().size());
    }

    @Test
    @DisplayName("getIntradayBars throws InvalidSymbolException for blank symbol")
    void rejectsBlankSymbol() {
        assertThrows(InvalidSymbolException.class, () -> service.getIntradayBars("  ", "5m"));
    }

    @Test
    @DisplayName("getIntradayBars throws InvalidSymbolException for null symbol")
    void rejectsNullSymbol() {
        assertThrows(InvalidSymbolException.class, () -> service.getIntradayBars(null, "5m"));
    }

    @Test
    @DisplayName("getIntradayBars throws InvalidSymbolException for invalid characters")
    void rejectsInvalidCharacters() {
        assertThrows(InvalidSymbolException.class, () -> service.getIntradayBars("VN@INDEX", "5m"));
    }

    private static BigDecimal bd(String value) {
        return new BigDecimal(value);
    }
}
