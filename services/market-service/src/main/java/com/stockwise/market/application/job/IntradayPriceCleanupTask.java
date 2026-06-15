package com.stockwise.market.application.job;

import com.stockwise.market.domain.repository.IntradayPriceRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

@Component
public class IntradayPriceCleanupTask {

    private static final Logger log = LoggerFactory.getLogger(IntradayPriceCleanupTask.class);

    private final IntradayPriceRepository intradayPriceRepository;

    public IntradayPriceCleanupTask(IntradayPriceRepository intradayPriceRepository) {
        this.intradayPriceRepository = intradayPriceRepository;
    }

    // Run every 15 minutes
    @Scheduled(fixedRate = 900000)
    @Transactional
    public void cleanupOldPrices() {
        log.info("Starting intraday price cleanup task...");
        Instant oneHourAgo = Instant.now().minus(1, ChronoUnit.HOURS);
        try {
            intradayPriceRepository.deleteOlderThan(oneHourAgo);
            log.info("Successfully cleaned up intraday prices older than {}", oneHourAgo);
        } catch (Exception e) {
            log.error("Error during intraday price cleanup", e);
        }
    }
}
