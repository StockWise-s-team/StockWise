package com.stockwise.portfolio.application.service.order;

import java.math.BigDecimal;

public final class OrderConstants {
    public static final BigDecimal INITIAL_CASH = new BigDecimal("100000000");
    public static final BigDecimal DEFAULT_ORDER_PRICE = new BigDecimal("150.00");

    public static final String BUY = "BUY";
    public static final String SELL = "SELL";

    public static final String PENDING = "PENDING";
    public static final String CANCELLED = "CANCELLED";

    private OrderConstants() {
    }
}
