package com.stockwise.order;

import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class OrderFactory {

    public Order pendingOrder(ValidatedOrderRequest request, Portfolio portfolio) {
        Order order = new Order();
        order.setUserId(request.userId());
        order.setPortfolioId(portfolio.getId());
        order.setSymbol(request.symbol());
        order.setType(request.type());
        order.setPrice(request.price());
        order.setQuantity(request.quantity());
        order.setStatus(OrderConstants.PENDING);
        order.setCreatedAt(LocalDateTime.now());
        return order;
    }
}
