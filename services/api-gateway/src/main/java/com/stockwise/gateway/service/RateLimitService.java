package com.stockwise.gateway.service;

import io.bucket4j.Bandwidth;
import io.bucket4j.Bucket;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
public class RateLimitService {

    private final Map<String, Bucket> authBuckets = new ConcurrentHashMap<>();

    public static final int AUTH_REQUESTS_PER_MINUTE = 10;
    public static final int AUTH_REQUESTS_PER_HOUR = 30;

    public boolean tryConsumeAuth(String key) {
        Bucket bucket = authBuckets.computeIfAbsent(key, this::createAuthBucket);
        boolean consumed = bucket.tryConsume(1);
        if (!consumed) {
            log.warn("Rate limit exceeded for key: {}", key);
        }
        return consumed;
    }

    private Bucket createAuthBucket(String key) {
        Bandwidth perMinute = Bandwidth.builder()
                .capacity(AUTH_REQUESTS_PER_MINUTE)
                .refillGreedy(AUTH_REQUESTS_PER_MINUTE, Duration.ofMinutes(1))
                .build();

        Bandwidth perHour = Bandwidth.builder()
                .capacity(AUTH_REQUESTS_PER_HOUR)
                .refillGreedy(AUTH_REQUESTS_PER_HOUR, Duration.ofHours(1))
                .build();

        return Bucket.builder()
                .addLimit(perMinute)
                .addLimit(perHour)
                .build();
    }
}
