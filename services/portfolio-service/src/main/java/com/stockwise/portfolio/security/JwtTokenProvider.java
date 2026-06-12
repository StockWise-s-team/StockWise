package com.stockwise.portfolio.security;

public interface JwtTokenProvider {
    boolean validateToken(String token);

    String getUserIdFromToken(String token);

    String getRoleFromToken(String token);

    String getTokenType(String token);
}
