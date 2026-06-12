package com.stockwise.portfolio.application.port.out;

import com.stockwise.portfolio.domain.entity.Order;

/**
 * Port interface for publishing order events.
 * Follows the Dependency Inversion Principle (DIP) and Single Responsibility Principle (SRP).
 */
public interface OrderEventPublisher {
    
    /**
     * Publishes an event when an order is created.
     *
     * @param order the created order
     */
    void publishOrderCreated(Order order);
    
    /**
     * Publishes an event when an order is cancelled.
     *
     * @param order the cancelled order
     */
    void publishOrderCancelled(Order order);
}
