package com.stockwise.user.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public record UserDto(
        UUID id,
        String email,
        String role,
        String fullName,
        LocalDateTime createdAt
) {}
