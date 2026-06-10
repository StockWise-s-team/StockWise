package com.stockwise.market.security;

public interface JwtTokenProvider {
    boolean validateToken(String token);
    String getUserIdFromToken(String token);
    String getRoleFromToken(String token);
    String getTokenId(String token);
    String getTokenType(String token);
}
