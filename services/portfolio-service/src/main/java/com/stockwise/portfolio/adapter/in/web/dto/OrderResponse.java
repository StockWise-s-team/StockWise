package com.stockwise.portfolio.adapter.in.web.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.UUID;

public record OrderResponse(
        @JsonProperty("order_id") UUID orderId,
        String status,
        String message
) {
}
