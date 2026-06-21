package com.stockwise.portfolio.application.service.order.reservation;

import com.stockwise.portfolio.application.service.order.ports.OrderReservationStrategy;
import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.application.service.order.ValidatedOrderRequest;
import com.stockwise.portfolio.application.exception.ConflictException;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

/**
 * Concrete reservation strategy for SELL orders.
 * Handles locking and releasing of holding share quantities in the user's portfolio.
 */
@Component
@RequiredArgsConstructor
public class SellOrderReservationStrategy implements OrderReservationStrategy {

    private final HoldingRepository holdingRepository;

    @Override
    public String orderType() {
        return OrderConstants.SELL;
    }

    /**
     * Locks/deducts the requested share quantity from the user's available holding shares.
     * Throws a ConflictException if the user doesn't own the stock or has insufficient shares.
     */
    @Override
    public void reserve(Portfolio portfolio, ValidatedOrderRequest request) {
        Holding holding = holdingRepository.findByPortfolioIdAndSymbol(portfolio.getId(), request.symbol())
                .orElseThrow(() -> new ConflictException("Insufficient holdings for SELL order"));
        if (holding.getQuantity() < request.quantity()) {
            throw new ConflictException("Insufficient holdings for SELL order");
        }
        holding.setQuantity(holding.getQuantity() - request.quantity());
        holdingRepository.save(holding);
    }

    /**
     * Unlocks and returns the locked shares back to the active holding entity on cancellation.
     */
    @Override
    public void release(Order order) {
        Holding holding = holdingRepository.findByPortfolioIdAndSymbol(order.getPortfolioId(), order.getSymbol())
                .orElseGet(() -> {
                    Holding newHolding = new Holding();
                    newHolding.setPortfolioId(order.getPortfolioId());
                    newHolding.setSymbol(order.getSymbol());
                    newHolding.setQuantity(0);
                    newHolding.setAvgPrice(order.getPrice());
                    return newHolding;
                });
        holding.setQuantity(holding.getQuantity() + order.getQuantity());
        holdingRepository.save(holding);
    }
}
