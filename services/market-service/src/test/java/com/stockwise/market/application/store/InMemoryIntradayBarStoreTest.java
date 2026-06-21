package com.stockwise.market.application.store;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class InMemoryIntradayBarStoreTest {

    private final InMemoryIntradayBarStore store = new InMemoryIntradayBarStore();

    @Test
    @DisplayName("upsert stores a new bar for unknown symbol")
    void upsertStoresNewBar() {
        Instant t = Instant.parse("2026-06-16T02:15:00Z");
        IntradayBar bar = new IntradayBar(t, bd("100"), bd("110"), bd("95"), bd("105"), 1000L, "5m");

        store.upsert("VHM", bar);

        var bars = store.getBars("VHM", "5m");
        assertEquals(1, bars.size());
        assertEquals(t, bars.get(0).barTime());
        assertEquals(0, bd("105").compareTo(bars.get(0).close()));
    }

    @Test
    @DisplayName("upsert merges bars with same barTime: high=max, low=min, volume=sum")
    void upsertMergesSameBarTime() {
        Instant t = Instant.parse("2026-06-16T02:15:00Z");
        store.upsert("VHM", new IntradayBar(t, bd("100"), bd("110"), bd("95"), bd("105"), 1000L, "5m"));
        store.upsert("VHM", new IntradayBar(t, bd("105"), bd("120"), bd("90"), bd("115"), 500L, "5m"));

        var bars = store.getBars("VHM", "5m");
        assertEquals(1, bars.size());
        IntradayBar merged = bars.get(0);
        assertEquals(0, bd("120").compareTo(merged.high()), "high should be max");
        assertEquals(0, bd("90").compareTo(merged.low()), "low should be min");
        assertEquals(1500L, merged.volume(), "volume should be sum");
        assertEquals(0, bd("100").compareTo(merged.open()), "open should keep first seen");
        assertEquals(0, bd("115").compareTo(merged.close()), "close should take latest");
    }

    @Test
    @DisplayName("getBars normalizes symbol case and filters by interval")
    void getBarsNormalizesAndFilters() {
        Instant t1 = Instant.parse("2026-06-16T02:15:00Z");
        Instant t2 = Instant.parse("2026-06-16T02:20:00Z");
        store.upsert("VHM", new IntradayBar(t1, bd("100"), bd("105"), bd("99"), bd("103"), 1L, "5m"));
        store.upsert("VHM", new IntradayBar(t2, bd("100"), bd("105"), bd("99"), bd("103"), 1L, "1m"));

        var fiveMin = store.getBars("vhm", "5m");
        var oneMin = store.getBars("VHM", "1m");
        var all = store.getBars("VHM", null);

        assertEquals(1, fiveMin.size());
        assertEquals(t1, fiveMin.get(0).barTime());
        assertEquals(1, oneMin.size());
        assertEquals(t2, oneMin.get(0).barTime());
        assertEquals(2, all.size());
    }

    @Test
    @DisplayName("getBars returns empty list for unknown symbol")
    void getBarsReturnsEmptyForUnknownSymbol() {
        var bars = store.getBars("XYZ", "5m");
        assertNotNull(bars);
        assertTrue(bars.isEmpty());
    }

    @Test
    @DisplayName("evictOlderThan removes bars older than cutoff")
    void evictOlderThanRemovesOldBars() {
        Instant old = Instant.parse("2026-06-15T02:00:00Z");
        Instant recent = Instant.parse("2026-06-16T02:00:00Z");
        store.upsert("VHM", new IntradayBar(old, bd("1"), bd("2"), bd("0"), bd("1"), 1L, "5m"));
        store.upsert("VHM", new IntradayBar(recent, bd("1"), bd("2"), bd("0"), bd("1"), 1L, "5m"));

        int removed = store.evictOlderThan(Instant.parse("2026-06-16T00:00:00Z"));

        assertEquals(1, removed);
        var bars = store.getBars("VHM", "5m");
        assertEquals(1, bars.size());
        assertEquals(recent, bars.get(0).barTime());
    }

    @Test
    @DisplayName("upsert is a no-op for null inputs")
    void upsertNullSafe() {
        store.upsert(null, new IntradayBar(Instant.now(), null, null, null, null, 0L, "5m"));
        store.upsert("VHM", null);
        store.upsert("VHM", new IntradayBar(null, null, null, null, null, 0L, "5m"));
        assertTrue(store.getBars("VHM", "5m").isEmpty());
    }

    private static BigDecimal bd(String value) {
        return new BigDecimal(value);
    }
}
