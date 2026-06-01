package com.stockwise.gateway.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockwise.gateway.security.JwtTokenProvider;
import com.stockwise.gateway.service.TokenBlacklistService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.util.Base64;

@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class LogoutController {

    private static final long ACCESS_TOKEN_TTL_MS = 900000;

    private final TokenBlacklistService tokenBlacklistService;
    private final JwtTokenProvider jwtTokenProvider;
    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${user-service.url}")
    private String userServiceUrl;

    @PostMapping("/logout")
    public ResponseEntity<?> logout(
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers) {

        String authHeader = headers.getFirst("Authorization");
        String accessToken = null;

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            accessToken = authHeader.substring(7);
        }

        String refreshToken = null;
        try {
            if (body != null && !body.isEmpty()) {
                JsonNode node = objectMapper.readTree(body);
                refreshToken = node.has("refreshToken") ? node.get("refreshToken").asText() : null;
            }
        } catch (Exception e) {
            log.warn("Could not parse logout body for refresh token");
        }

        if (accessToken != null) {
            if (jwtTokenProvider.validateToken(accessToken)) {
                String tokenJti = jwtTokenProvider.getTokenId(accessToken);
                long ttlMs = extractTtl(accessToken);
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
            headers.forEach((key, values) -> {
                if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Host")) {
                    upstreamHeaders.addAll(key, values);
                }
            });
            HttpEntity<String> entity = new HttpEntity<>(body, upstreamHeaders);
            restTemplate.exchange(userServiceUrl + "/auth/logout", HttpMethod.POST, entity, String.class);
        } catch (Exception e) {
            log.warn("Could not forward logout to user-service: {}", e.getMessage());
        }

        return ResponseEntity.ok().build();
    }

    private long extractTtl(String token) {
        try {
            String[] parts = token.split("\\.");
            if (parts.length == 3) {
                String payload = new String(Base64.getUrlDecoder().decode(parts[1]));
                JsonNode node = objectMapper.readTree(payload);
                long exp = node.get("exp").asLong();
                long now = System.currentTimeMillis() / 1000;
                return Math.max(0, (exp - now) * 1000);
            }
        } catch (Exception e) {
            log.warn("Could not extract TTL from token, using default");
        }
        return ACCESS_TOKEN_TTL_MS;
    }
}
