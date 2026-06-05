package com.stockwise.order.reservation;

import com.stockwise.order.OrderConstants;
import com.stockwise.order.ValidatedOrderRequest;
import com.stockwise.portfolio.application.exception.ConflictException;
import com.stockwise.portfolio.application.exception.NotFoundException;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
@RequiredArgsConstructor
public class BuyOrderReservationStrategy implements OrderReservationStrategy {

    private final PortfolioRepository portfolioRepository;

    @Override
    public String orderType() {
        return OrderConstants.BUY;
    }

    @Override
    public void reserve(Portfolio portfolio, ValidatedOrderRequest request) {
        BigDecimal cost = request.price().multiply(BigDecimal.valueOf(request.quantity()));
        if (portfolio.getVirtualCash().compareTo(cost) < 0) {
            throw new ConflictException("Insufficient cash for BUY order");
        }
        portfolio.setVirtualCash(portfolio.getVirtualCash().subtract(cost));
        portfolioRepository.save(portfolio);
    }

    @Override
    public void release(Order order) {
        Portfolio portfolio = portfolioRepository.findById(order.getPortfolioId())
                .orElseThrow(() -> new NotFoundException("Portfolio not found"));
        BigDecimal amount = order.getPrice().multiply(BigDecimal.valueOf(order.getQuantity()));
        portfolio.setVirtualCash(portfolio.getVirtualCash().add(amount));
        portfolioRepository.save(portfolio);
    }
}
