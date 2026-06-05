package com.stockwise.order.reservation;

import com.stockwise.order.ValidatedOrderRequest;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;

public interface OrderReservationStrategy {
    String orderType();

    void reserve(Portfolio portfolio, ValidatedOrderRequest request);

    void release(Order order);
}
