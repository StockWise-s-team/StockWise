package com.stockwise.market.application.store;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentSkipListMap;

@Component
public class InMemoryIntradayBarStore {

    private final ConcurrentHashMap<String, ConcurrentSkipListMap<Instant, IntradayBar>> barsBySymbol = new ConcurrentHashMap<>();

    public void upsert(String symbol, IntradayBar bar) {
        if (symbol == null || bar == null || bar.barTime() == null) {
            return;
        }
        String normalizedSymbol = symbol.trim().toUpperCase();
        ConcurrentSkipListMap<Instant, IntradayBar> symbolMap = barsBySymbol
                .computeIfAbsent(normalizedSymbol, k -> new ConcurrentSkipListMap<>());
        symbolMap.merge(bar.barTime(), bar, InMemoryIntradayBarStore::mergeBars);
    }

    public List<IntradayBar> getBars(String symbol, String interval) {
        if (symbol == null) {
            return List.of();
        }
        String normalizedSymbol = symbol.trim().toUpperCase();
        ConcurrentSkipListMap<Instant, IntradayBar> symbolMap = barsBySymbol.get(normalizedSymbol);
        if (symbolMap == null || symbolMap.isEmpty()) {
            return List.of();
        }
        List<IntradayBar> out = new ArrayList<>();
        for (IntradayBar bar : symbolMap.values()) {
            if (interval == null || interval.isBlank() || interval.equals(bar.interval())) {
                out.add(bar);
            }
        }
        return out;
    }

    public List<IntradayBar> getBarsFrom(String symbol, String interval, Instant from) {
        if (symbol == null || from == null) {
            return List.of();
        }
        List<IntradayBar> all = getBars(symbol, interval);
        if (all.isEmpty()) {
            return Collections.emptyList();
        }
        List<IntradayBar> out = new ArrayList<>();
        for (IntradayBar b : all) {
            if (!b.barTime().isBefore(from)) {
                out.add(b);
            }
        }
        return out;
    }

    public int evictOlderThan(Instant cutoff) {
        if (cutoff == null) {
            return 0;
        }
        int removed = 0;
        for (ConcurrentSkipListMap<Instant, IntradayBar> symbolMap : barsBySymbol.values()) {
            int sizeBefore = symbolMap.size();
            symbolMap.headMap(cutoff, true).clear();
            removed += sizeBefore - symbolMap.size();
            if (symbolMap.isEmpty()) {
                barsBySymbol.values().remove(symbolMap);
            }
        }
        return removed;
    }

    public void clearSymbol(String symbol) {
        if (symbol == null) {
            return;
        }
        barsBySymbol.remove(symbol.trim().toUpperCase());
    }

    private static IntradayBar mergeBars(IntradayBar existing, IntradayBar incoming) {
        BigDecimal high = max(existing.high(), incoming.high());
        BigDecimal low = min(existing.low(), incoming.low());
        long volume = (existing.volume() == null ? 0L : existing.volume())
                + (incoming.volume() == null ? 0L : incoming.volume());
        BigDecimal open = existing.open() != null ? existing.open() : incoming.open();
        BigDecimal close = incoming.close() != null ? incoming.close() : existing.close();
        String interval = existing.interval() == null ? incoming.interval() : existing.interval();
        return new IntradayBar(existing.barTime(), open, high, low, close, volume, interval);
    }

    private static BigDecimal max(BigDecimal a, BigDecimal b) {
        if (a == null) return b;
        if (b == null) return a;
        return a.compareTo(b) >= 0 ? a : b;
    }

    private static BigDecimal min(BigDecimal a, BigDecimal b) {
        if (a == null) return b;
        if (b == null) return a;
        return a.compareTo(b) <= 0 ? a : b;
    }
}
