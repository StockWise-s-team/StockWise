package com.stockwise.user.adapter.out.persistence;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;

@Slf4j
@Service
@RequiredArgsConstructor
public class TokenManagementService {

    private static final String REFRESH_TOKEN_PREFIX = "refresh:valid:";
    private static final String ACCESS_TOKEN_BLACKLIST_PREFIX = "token:blacklist:";

    private final StringRedisTemplate redisTemplate;

    public void registerRefreshToken(String jti, String userId, Duration ttl) {
        String key = REFRESH_TOKEN_PREFIX + jti;
        redisTemplate.opsForValue().set(key, userId, ttl);
        log.debug("Registered refresh token JTI: {} for user: {}", jti, userId);
    }

    public boolean isRefreshTokenValid(String jti) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(REFRESH_TOKEN_PREFIX + jti));
    }

    public void revokeRefreshToken(String jti) {
        redisTemplate.delete(REFRESH_TOKEN_PREFIX + jti);
        log.debug("Revoked refresh token JTI: {}", jti);
    }

    public void blacklistAccessToken(String jti, Duration ttl) {
        redisTemplate.opsForValue().set(ACCESS_TOKEN_BLACKLIST_PREFIX + jti, "1", ttl);
        log.debug("Blacklisted access token JTI: {}", jti);
    }

    public boolean isAccessTokenBlacklisted(String jti) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(ACCESS_TOKEN_BLACKLIST_PREFIX + jti));
    }
}
