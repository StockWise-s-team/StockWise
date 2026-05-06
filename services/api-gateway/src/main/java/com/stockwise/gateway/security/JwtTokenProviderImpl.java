package com.stockwise.gateway.security;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Date;
import java.util.UUID;

@Slf4j
@Component
public class JwtTokenProviderImpl implements JwtTokenProvider {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.access-token-expiration}")
    private long accessTokenExpiration;

    @Value("${jwt.refresh-token-expiration}")
    private long refreshTokenExpiration;

    @Override
    public String generateAccessToken(String userId, String email, String role) {
        long now = System.currentTimeMillis();
        long exp = now + accessTokenExpiration;
        String payload = userId + ":" + email + ":" + role + ":" + now + ":" + exp;
        String signature = hmacSha256(payload, secret);
        return Base64.getEncoder().encodeToString((payload + "." + signature).getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public String generateRefreshToken(String userId) {
        long now = System.currentTimeMillis();
        long exp = now + refreshTokenExpiration;
        String payload = userId + ":" + UUID.randomUUID() + ":" + now + ":" + exp;
        String signature = hmacSha256(payload, secret);
        return Base64.getEncoder().encodeToString((payload + "." + signature).getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public boolean validateToken(String token) {
        try {
            String decoded = new String(Base64.getDecoder().decode(token), StandardCharsets.UTF_8);
            String[] parts = decoded.split("\\.");
            if (parts.length != 2) return false;
            String payload = parts[0];
            String providedSignature = parts[1];
            String expectedSignature = hmacSha256(payload, secret);
            if (!providedSignature.equals(expectedSignature)) return false;
            String[] fields = payload.split(":");
            long exp = Long.parseLong(fields[fields.length - 1]);
            return System.currentTimeMillis() < exp;
        } catch (Exception e) {
            log.warn("Token validation failed: {}", e.getMessage());
            return false;
        }
    }

    @Override
    public String getUserIdFromToken(String token) {
        try {
            String decoded = new String(Base64.getDecoder().decode(token), StandardCharsets.UTF_8);
            String payload = decoded.split("\\.")[0];
            return payload.split(":")[0];
        } catch (Exception e) {
            log.warn("Failed to extract userId from token: {}", e.getMessage());
            return null;
        }
    }

    private String hmacSha256(String data, String secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec spec = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(spec);
            byte[] hash = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) {
            throw new RuntimeException("Failed to sign token", e);
        }
    }
}
