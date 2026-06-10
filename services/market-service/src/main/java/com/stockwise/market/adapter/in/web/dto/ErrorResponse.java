package com.stockwise.market.adapter.in.web.dto;

import java.time.LocalDateTime;

public record ErrorResponse(String error, String message, LocalDateTime timestamp) {
}
