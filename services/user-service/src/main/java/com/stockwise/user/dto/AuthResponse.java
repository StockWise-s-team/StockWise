package com.stockwise.user.dto;

public record AuthResponse(
        String accessToken,
        String refreshToken
) {}
