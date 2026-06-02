package com.stockwise.portfolio.adapter.in.web;

import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.UUID;

@Component
public class UserIdResolver {

    public UUID resolve(String userIdHeader, String userIdParam) {
        return Optional.ofNullable(userIdHeader)
                .or(() -> Optional.ofNullable(userIdParam))
                .filter(value -> !value.isBlank())
                .map(UUID::fromString)
                .orElseThrow(() -> new IllegalArgumentException("userId is required for order cancellation"));
    }
}
