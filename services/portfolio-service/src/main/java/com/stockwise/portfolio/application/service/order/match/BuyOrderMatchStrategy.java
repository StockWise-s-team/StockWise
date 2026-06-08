package com.stockwise.portfolio.application.service.order.match;

import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * Concrete match strategy for BUY orders.
 * Handles the actual asset changes when a buy order is filled:
 * - Calculates and refunds excess frozen cash to virtual cash if matched at a lower price.
 * - Increments holding shares and recalculates the weighted average purchase price.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class BuyOrderMatchStrategy implements OrderMatchStrategy {

    private final PortfolioRepository portfolioRepository;
    private final HoldingRepository holdingRepository;

    @Override
    public String orderType() {
        return OrderConstants.BUY;
    }

    /**
     * Executes buy match transactions:
     * 1. Refunds any price improvement cash back to the virtual cash balance.
     * 2. Recalculates the holding's weighted average price: (oldQty * oldAvg + matchedQty * matchPrice) / newQty.
     * 3. Increases holding quantity.
     */
    @Override
    public void match(Portfolio portfolio, Order order, BigDecimal matchPrice) {
        // If matchPrice is lower than ordered price, refund the difference
        if (matchPrice.compareTo(order.getPrice()) < 0) {
            BigDecimal orderCost = order.getPrice().multiply(BigDecimal.valueOf(order.getQuantity()));
            BigDecimal actualCost = matchPrice.multiply(BigDecimal.valueOf(order.getQuantity()));
            BigDecimal refund = orderCost.subtract(actualCost);
            portfolio.setVirtualCash(portfolio.getVirtualCash().add(refund));
            portfolioRepository.save(portfolio);
            log.info("Refunded {} to portfolio {} due to lower match price", refund, portfolio.getId());
        }

        // Add holdings and calculate new average purchase price
        Holding holding = holdingRepository.findByPortfolioIdAndSymbol(portfolio.getId(), order.getSymbol())
                .orElseGet(() -> {
                    Holding newHolding = new Holding();
                    newHolding.setPortfolioId(portfolio.getId());
                    newHolding.setSymbol(order.getSymbol());
                    newHolding.setQuantity(0);
                    newHolding.setAvgPrice(BigDecimal.ZERO);
                    return newHolding;
                });

        int oldQty = holding.getQuantity();
        BigDecimal oldAvg = holding.getAvgPrice() != null ? holding.getAvgPrice() : BigDecimal.ZERO;
        int newQty = oldQty + order.getQuantity();

        BigDecimal oldTotalCost = oldAvg.multiply(BigDecimal.valueOf(oldQty));
        BigDecimal newTotalCost = matchPrice.multiply(BigDecimal.valueOf(order.getQuantity()));
        BigDecimal avgPrice = oldTotalCost.add(newTotalCost).divide(BigDecimal.valueOf(newQty), 4, RoundingMode.HALF_UP);

        holding.setQuantity(newQty);
        holding.setAvgPrice(avgPrice);
        holdingRepository.save(holding);
        log.info("Updated holding for symbol {} in portfolio {}: quantity={}, avgPrice={}", order.getSymbol(), portfolio.getId(), newQty, avgPrice);
    }
}
