package com.stockwise.gateway.config;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;

@Slf4j
@Component
public class JwtSecretValidator {

    private static final int MIN_SECRET_LENGTH = 32;

    @Value("${jwt.secret}")
    private String jwtSecret;

    @PostConstruct
    public void validate() {
        if (jwtSecret == null || jwtSecret.isBlank()) {
            throw new IllegalStateException(
                    "JWT_SECRET environment variable is not set. " +
                    "Set a strong secret (at least 32 characters) via the JWT_SECRET env var.");
        }
        if (jwtSecret.getBytes(StandardCharsets.UTF_8).length < MIN_SECRET_LENGTH) {
            throw new IllegalStateException(
                    "JWT_SECRET is too short (" + jwtSecret.length() + " bytes). " +
                    "A minimum of " + MIN_SECRET_LENGTH + " bytes (characters in UTF-8) is required.");
        }
        if (jwtSecret.contains("change-in-production") || jwtSecret.contains("dev-secret")) {
            throw new IllegalStateException(
                    "JWT_SECRET contains a placeholder value. " +
                    "Replace 'stockwise-dev-secret-key-change-in-production' with a real secret.");
        }
        log.info("JWT secret validated successfully");
    }
}
