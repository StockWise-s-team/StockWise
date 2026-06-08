package com.stockwise.portfolio.application.port.out;

import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import java.math.BigDecimal;

/**
 * Port interface for publishing portfolio updated events.
 * Follows the Dependency Inversion Principle (DIP) and Single Responsibility Principle (SRP).
 */
public interface PortfolioEventPublisher {
    
    /**
     * Publishes an event when a portfolio has been updated due to a matched order.
     *
     * @param portfolio  the updated portfolio
     * @param order      the matched order
     * @param matchPrice the actual matched price
     */
    void publishPortfolioUpdated(Portfolio portfolio, Order order, BigDecimal matchPrice);
}
