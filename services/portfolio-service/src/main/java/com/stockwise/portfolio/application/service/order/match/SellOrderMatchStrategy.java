package com.stockwise.portfolio.application.service.order.match;

import com.stockwise.portfolio.application.service.order.ports.OrderMatchStrategy;
import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

/**
 * Concrete match strategy for SELL orders.
 * Handles the actual asset changes when a sell order is filled:
 * - Adds the actual sale proceeds (matchPrice * quantity) back to the virtual cash balance.
 * - Deletes the holding entry if the remaining share quantity reaches zero.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class SellOrderMatchStrategy implements OrderMatchStrategy {

    private final PortfolioRepository portfolioRepository;
    private final HoldingRepository holdingRepository;

    @Override
    public String orderType() {
        return OrderConstants.SELL;
    }

    /**
     * Executes sell match transactions:
     * 1. Calculates cash proceeds (matchPrice * quantity) and adds it to virtual cash.
     * 2. Cleans up empty holding objects from database if no shares remain (held shares were already deducted on reserve).
     */
    @Override
    public void match(Portfolio portfolio, Order order, BigDecimal matchPrice) {
        // Add proceeds to portfolio cash (holdings were already deducted on reservation)
        BigDecimal proceeds = matchPrice.multiply(BigDecimal.valueOf(order.getQuantity()));
        portfolio.setVirtualCash(portfolio.getVirtualCash().add(proceeds));
        portfolioRepository.save(portfolio);

        // Delete holding if quantity became 0
        holdingRepository.findByPortfolioIdAndSymbol(portfolio.getId(), order.getSymbol())
                .ifPresent(holding -> {
                    if (holding.getQuantity() == 0) {
                        holdingRepository.delete(holding);
                        log.info("Deleted empty holding for symbol {} in portfolio {}", order.getSymbol(), portfolio.getId());
                    }
                });

        log.info("Added sell proceeds {} to portfolio {}", proceeds, portfolio.getId());
    }
}
