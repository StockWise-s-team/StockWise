package com.stockwise.gateway.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;

@Slf4j
@Service
@RequiredArgsConstructor
public class TokenBlacklistService {

    private static final String BLACKLIST_PREFIX = "token:blacklist:";
    private static final String REFRESH_TOKEN_PREFIX = "refresh:valid:";

    private final StringRedisTemplate redisTemplate;

    public void blacklistAccessToken(String tokenJti, Duration ttl) {
        String key = BLACKLIST_PREFIX + tokenJti;
        redisTemplate.opsForValue().set(key, "1", ttl);
        log.debug("Blacklisted access token JTI: {}", tokenJti);
    }

    public boolean isAccessTokenBlacklisted(String tokenJti) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(BLACKLIST_PREFIX + tokenJti));
    }

    public void revokeRefreshToken(String refreshTokenJti) {
        String key = REFRESH_TOKEN_PREFIX + refreshTokenJti;
        redisTemplate.delete(key);
        log.debug("Revoked refresh token JTI: {}", refreshTokenJti);
    }

    public void registerRefreshToken(String refreshTokenJti, String userId, Duration ttl) {
        String key = REFRESH_TOKEN_PREFIX + refreshTokenJti;
        redisTemplate.opsForValue().set(key, userId, ttl);
        log.debug("Registered refresh token JTI: {} for user: {}", refreshTokenJti, userId);
    }

    public boolean isRefreshTokenValid(String refreshTokenJti) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(REFRESH_TOKEN_PREFIX + refreshTokenJti));
    }
}
