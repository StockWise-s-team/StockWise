package com.stockwise.portfolio.application.service.order.ports;

import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;

import java.math.BigDecimal;

/**
 * Strategy interface for executing order matching processes (DIP/OCP).
 * Different strategies are chosen depending on whether the order type is BUY or SELL:
 * - BUY strategy adds shares to holdings and refunds excess cash if matched price is lower.
 * - SELL strategy adds proceeds to virtual cash and handles reduction/deletion of shares in holdings.
 */
public interface OrderMatchStrategy {
    
    /**
     * The order type (BUY/SELL) that this strategy processes.
     *
     * @return the order type string
     */
    String orderType();
    
    /**
     * Executes the matching operations for a matched order.
     *
     * @param portfolio  the user's portfolio entity
     * @param order      the order entity being matched
     * @param matchPrice the actual execution price of the match
     */
    void match(Portfolio portfolio, Order order, BigDecimal matchPrice);
}
