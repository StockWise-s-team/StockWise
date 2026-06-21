package com.stockwise.market.adapter.in.web.dto;

import java.time.Instant;
import java.util.List;

public record IntradayOhlcResponse(
        String symbol,
        String interval,
        List<IntradayOhlcBarResponse> data,
        Instant asOf
) {
}
