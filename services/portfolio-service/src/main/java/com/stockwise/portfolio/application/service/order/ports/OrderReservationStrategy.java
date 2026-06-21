package com.stockwise.portfolio.application.service.order.ports;

import com.stockwise.portfolio.application.service.order.ValidatedOrderRequest;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;

/**
 * Strategy interface for reserving and releasing assets associated with orders (DIP/OCP).
 * Different strategies are chosen depending on whether the order type is BUY or SELL:
 * - BUY strategy reserves/releases virtual cash.
 * - SELL strategy reserves/releases holding shares.
 */
public interface OrderReservationStrategy {
    
    /**
     * The order type (BUY/SELL) that this strategy processes.
     *
     * @return the order type string
     */
    String orderType();

    /**
     * Reserves assets (cash or shares) in the user's portfolio when placing a PENDING order.
     * Throws a BadRequestException if assets are insufficient.
     *
     * @param portfolio the user's portfolio entity
     * @param request   the validated order placement request details
     */
    void reserve(Portfolio portfolio, ValidatedOrderRequest request);

    /**
     * Releases (unfreezes) assets when an order is cancelled or matched with refund.
     *
     * @param order the order entity to release assets for
     */
    void release(Order order);
}
