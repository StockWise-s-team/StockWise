package com.stockwise.market.application.job;

import com.stockwise.market.application.store.InMemoryIntradayBarStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;

@Component
public class IntradayBarEvictionTask {

    private static final Logger log = LoggerFactory.getLogger(IntradayBarEvictionTask.class);

    private final InMemoryIntradayBarStore barStore;

    public IntradayBarEvictionTask(InMemoryIntradayBarStore barStore) {
        this.barStore = barStore;
    }

    @Scheduled(cron = "0 1 0 * * *")
    public void evictPreviousDayBars() {
        Instant cutoff = LocalDate.now(ZoneOffset.UTC)
                .atStartOfDay(ZoneOffset.UTC)
                .toInstant();
        try {
            int removed = barStore.evictOlderThan(cutoff);
            log.info("Intraday bar eviction completed: removed {} bars older than {}", removed, cutoff);
        } catch (Exception e) {
            log.error("Intraday bar eviction failed", e);
        }
    }
}
