package com.stockwise.gateway.controller;

import com.stockwise.gateway.security.JwtTokenProvider;
import com.stockwise.gateway.service.TokenBlacklistService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;

@Controller
@RequestMapping("/auth")
@RequiredArgsConstructor
@Slf4j
public class LogoutController {

    private static final long ACCESS_TOKEN_TTL_MS = 900000;
    private static final String REFRESH_TOKEN_COOKIE = "refresh_token";

    private final TokenBlacklistService tokenBlacklistService;
    private final JwtTokenProvider jwtTokenProvider;
    private final WebClient webClient;

    @Value("${user-service.url}")
    private String userServiceUrl;

    @PostMapping("/logout")
    public ResponseEntity<?> logout(@RequestHeader HttpHeaders headers) {
        String authHeader = headers.getFirst("Authorization");
        String accessToken = null;

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            accessToken = authHeader.substring(7);
        }

        String cookieHeader = headers.getFirst("Cookie");
        String refreshToken = extractRefreshTokenFromCookie(cookieHeader);

        if (accessToken != null) {
            if (jwtTokenProvider.validateToken(accessToken)) {
                String tokenJti = jwtTokenProvider.getTokenId(accessToken);
                long ttlMs = extractTtlFromProvider(accessToken);
                tokenBlacklistService.blacklistAccessToken(tokenJti, Duration.ofMillis(ttlMs));
                log.info("Access token blacklisted on logout");
            }
        }

        if (refreshToken != null) {
            if (jwtTokenProvider.validateToken(refreshToken)) {
                String refreshJti = jwtTokenProvider.getRefreshTokenJti(refreshToken);
                if (refreshJti != null) {
                    tokenBlacklistService.revokeRefreshToken(refreshJti);
                    log.info("Refresh token revoked on logout");
                }
            }
        }

        try {
            HttpHeaders upstreamHeaders = new HttpHeaders();
            upstreamHeaders.setContentType(MediaType.APPLICATION_JSON);
            upstreamHeaders.add("Cookie", "refresh_token=" + (refreshToken != null ? refreshToken : ""));
            headers.forEach((key, values) -> {
                if (!key.equalsIgnoreCase("Content-Length")
                        && !key.equalsIgnoreCase("Host")
                        && !key.equalsIgnoreCase("Cookie")) {
                    upstreamHeaders.addAll(key, values);
                }
            });

            String body = refreshToken != null
                    ? "{\"refreshToken\":\"" + refreshToken + "\"}"
                    : "{}";

            webClient.post()
                    .uri(userServiceUrl + "/auth/logout")
                    .headers(h -> h.addAll(upstreamHeaders))
                    .bodyValue(body)
                    .retrieve()
                    .toEntity(String.class)
                    .timeout(Duration.ofSeconds(5))
                    .block();
        } catch (Exception e) {
            log.warn("Could not forward logout to user-service: {}", e.getMessage());
        }

        return ResponseEntity.ok().build();
    }

    private long extractTtlFromProvider(String token) {
        try {
            long expMs = jwtTokenProvider.getExpiration(token);
            return Math.max(0, expMs - System.currentTimeMillis());
        } catch (Exception e) {
            log.warn("Could not extract TTL from token, using default");
            return ACCESS_TOKEN_TTL_MS;
        }
    }

    private String extractRefreshTokenFromCookie(String cookieHeader) {
        if (cookieHeader == null || cookieHeader.isEmpty()) {
            return null;
        }
        for (String part : cookieHeader.split(";")) {
            String trimmed = part.trim();
            if (trimmed.startsWith(REFRESH_TOKEN_COOKIE + "=")) {
                return trimmed.substring(REFRESH_TOKEN_COOKIE.length() + 1);
            }
        }
        return null;
    }
}
