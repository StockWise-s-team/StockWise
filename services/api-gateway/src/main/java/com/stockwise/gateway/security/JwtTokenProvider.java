package com.stockwise.gateway.security;

public interface JwtTokenProvider {
    String generateAccessToken(String userId, String email, String role);
    String generateRefreshToken(String userId);
    boolean validateToken(String token);
    String getUserIdFromToken(String token);
}
