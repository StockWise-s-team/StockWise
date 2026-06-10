package com.stockwise.portfolio.application.service.order;

import com.stockwise.portfolio.application.service.order.match.OrderMatchStrategyRegistry;
import com.stockwise.portfolio.application.port.out.PortfolioEventPublisher;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;
import com.stockwise.portfolio.domain.repository.OrderRepository;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import com.stockwise.portfolio.domain.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Processor for order matching.
 * Adheres to SOLID design principles by delegating match executions to matching strategies
 * and event publishing to a specialized publisher.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderMatchProcessor {

    private final OrderRepository orderRepository;
    private final PortfolioRepository portfolioRepository;
    private final TransactionRepository transactionRepository;
    private final OrderMatchStrategyRegistry matchStrategyRegistry;
    private final PortfolioEventPublisher portfolioEventPublisher;

    @Transactional
    public void matchPendingOrders(String symbol, BigDecimal price) {
        java.util.List<Order> pendingOrders = orderRepository.findBySymbolAndStatus(symbol, OrderConstants.PENDING);
        log.info("Found {} PENDING orders for symbol {}", pendingOrders.size(), symbol);
        
        for (Order order : pendingOrders) {
            boolean isMatch = false;
            if (OrderConstants.BUY.equals(order.getType())) {
                isMatch = order.getPrice().compareTo(price) >= 0;
            } else if (OrderConstants.SELL.equals(order.getType())) {
                isMatch = order.getPrice().compareTo(price) <= 0;
            }

            if (isMatch) {
                try {
                    processMatch(order, price);
                } catch (Exception e) {
                    log.error("Failed to process match for order {}: {}", order.getId(), e.getMessage(), e);
                }
            }
        }
    }

    @Transactional
    public void processMatch(Order order, BigDecimal matchPrice) {
        if (!OrderConstants.PENDING.equals(order.getStatus())) {
            log.warn("Order {} is not PENDING (current status: {}). Skipping match.", order.getId(), order.getStatus());
            return;
        }

        log.info("Processing match for order {} of symbol {} at price {}", order.getId(), order.getSymbol(), matchPrice);

        Portfolio portfolio = portfolioRepository.findById(order.getPortfolioId())
                .orElseThrow(() -> new IllegalStateException("Portfolio not found for ID: " + order.getPortfolioId()));

        // Execute matching strategy based on order type (DIP/OCP compliant)
        matchStrategyRegistry.get(order.getType()).match(portfolio, order, matchPrice);

        // 1. Create transaction record
        Transaction transaction = new Transaction();
        transaction.setPortfolioId(order.getPortfolioId());
        transaction.setSymbol(order.getSymbol());
        transaction.setType(order.getType());
        transaction.setQuantity(order.getQuantity());
        transaction.setPrice(matchPrice);
        transaction.setExecutedAt(LocalDateTime.now());
        transactionRepository.save(transaction);

        // 2. Update order status
        order.setStatus("FILLED");
        orderRepository.save(order);

        // 3. Publish portfolio updated event via publisher abstraction
        portfolioEventPublisher.publishPortfolioUpdated(portfolio, order, matchPrice);
    }
}
