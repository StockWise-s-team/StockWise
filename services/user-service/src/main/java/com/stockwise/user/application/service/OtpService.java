package com.stockwise.user.application.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.time.Duration;

/**
 * Service responsible for OTP lifecycle: generation, storage in Redis, verification, and deletion.
 * Key format: password-reset:{email}
 * TTL: 5 minutes
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OtpService {

    private static final String OTP_KEY_PREFIX = "password-reset:";
    private static final Duration OTP_TTL = Duration.ofMinutes(5);
    private static final int OTP_LENGTH = 6;

    private final StringRedisTemplate redisTemplate;
    private final SecureRandom secureRandom = new SecureRandom();

    /**
     * Generates a 6-digit OTP, stores it in Redis with a 5-minute TTL, and returns it.
     */
    public String generateAndStoreOtp(String email) {
        String otp = String.format("%06d", secureRandom.nextInt(1_000_000));
        String key = buildKey(email);
        redisTemplate.opsForValue().set(key, otp, OTP_TTL);
        log.info("OTP stored for email: {} (TTL: {} min)", email, OTP_TTL.toMinutes());
        return otp;
    }

    /**
     * Verifies the OTP for a given email. Returns true if valid and matches; false otherwise.
     * Does NOT delete the OTP — call deleteOtp() explicitly after a successful password reset.
     */
    public boolean verifyOtp(String email, String otp) {
        String key = buildKey(email);
        String stored = redisTemplate.opsForValue().get(key);
        if (stored == null) {
            log.warn("OTP not found or expired for email: {}", email);
            return false;
        }
        boolean matches = stored.equals(otp);
        if (!matches) {
            log.warn("OTP mismatch for email: {}", email);
        }
        return matches;
    }

    /**
     * Deletes the OTP from Redis (call after a successful password reset).
     */
    public void deleteOtp(String email) {
        redisTemplate.delete(buildKey(email));
        log.info("OTP deleted for email: {}", email);
    }

    private String buildKey(String email) {
        return OTP_KEY_PREFIX + email;
    }
}
