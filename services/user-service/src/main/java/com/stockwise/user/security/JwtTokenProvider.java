package com.stockwise.user.security;

public interface JwtTokenProvider {
    String generateAccessToken(String userId, String email, String role);
    String generateRefreshToken(String userId);
    boolean validateToken(String token);
    String getUserIdFromToken(String token);
    String getEmailFromToken(String token);
    String getRoleFromToken(String token);
    String getTokenId(String token);
    String getRefreshTokenJti(String token);
}
