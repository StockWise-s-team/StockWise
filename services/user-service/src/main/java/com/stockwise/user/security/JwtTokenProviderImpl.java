package com.stockwise.user.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Date;
import java.util.UUID;

@Slf4j
@Component
public class JwtTokenProviderImpl implements JwtTokenProvider {

    private final SecretKey secretKey;
    private final long accessTokenExpirationMs;
    private final long refreshTokenExpirationMs;

    public JwtTokenProviderImpl(
            @Value("${jwt.secret}") String secret,
            @Value("${jwt.access-token-expiration}") long accessTokenExpirationMs,
            @Value("${jwt.refresh-token-expiration}") long refreshTokenExpirationMs) {
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.accessTokenExpirationMs = accessTokenExpirationMs;
        this.refreshTokenExpirationMs = refreshTokenExpirationMs;
    }

    @Override
    public String generateAccessToken(String userId, String email, String role) {
        Date now = new Date();
        Date exp = new Date(now.getTime() + accessTokenExpirationMs);

        return Jwts.builder()
                .subject(userId)
                .claim("email", email)
                .claim("role", role)
                .claim("type", "access")
                .id(UUID.randomUUID().toString())
                .issuedAt(now)
                .expiration(exp)
                .signWith(secretKey)
                .compact();
    }

    @Override
    public String generateRefreshToken(String userId) {
        Date now = new Date();
        Date exp = new Date(now.getTime() + refreshTokenExpirationMs);

        return Jwts.builder()
                .subject(userId)
                .claim("type", "refresh")
                .claim("jti", UUID.randomUUID().toString())
                .issuedAt(now)
                .expiration(exp)
                .signWith(secretKey)
                .compact();
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
    public String getEmailFromToken(String token) {
        return getClaims(token).get("email", String.class);
    }

    @Override
    public String getRoleFromToken(String token) {
        return getClaims(token).get("role", String.class);
    }

    private Claims getClaims(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
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
    public String getRefreshTokenJti(String token) {
        Claims claims = getClaims(token);
        return claims.get("jti", String.class);
    }

    @Override
    public String getTokenType(String token) {
        Claims claims = getClaims(token);
        String type = claims.get("type", String.class);
        return type != null ? type : "unknown";
    }

    @Override
    public long getExpiration(String token) {
        Claims claims = getClaims(token);
        return claims.getExpiration().getTime();
    }
}
