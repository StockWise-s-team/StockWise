package com.stockwise.market.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

@Component
public class JwtTokenProviderImpl implements JwtTokenProvider {

    private static final Logger log = LoggerFactory.getLogger(JwtTokenProviderImpl.class);
    private final SecretKey secretKey;

    public JwtTokenProviderImpl(@Value("${jwt.secret}") String secret) {
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                    .verifyWith(secretKey)
                    .build()
                    .parseSignedClaims(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            log.warn("JWT validation failed: {}", e.getMessage());
            return false;
        }
    }

    @Override
    public String getUserIdFromToken(String token) {
        return getClaims(token).getSubject();
    }

    @Override
    public String getRoleFromToken(String token) {
        return getClaims(token).get("role", String.class);
    }

    @Override
    public String getTokenId(String token) {
        Claims claims = getClaims(token);
        String jti = claims.getId();
        if (jti != null) {
            return jti;
        }
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(token.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not available", e);
        }
    }

    @Override
    public String getTokenType(String token) {
        Claims claims = getClaims(token);
        String type = claims.get("type", String.class);
        return type != null ? type : "unknown";
    }

    private Claims getClaims(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
