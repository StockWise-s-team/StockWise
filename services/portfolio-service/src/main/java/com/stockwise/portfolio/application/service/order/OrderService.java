package com.stockwise.portfolio.application.service.order;

import com.stockwise.portfolio.application.exception.BadRequestException;
import com.stockwise.portfolio.application.exception.ConflictException;
import com.stockwise.portfolio.application.exception.NotFoundException;
import com.stockwise.portfolio.application.port.in.CancelOrderUseCase;
import com.stockwise.portfolio.application.port.in.PlaceOrderUseCase;
import com.stockwise.portfolio.application.service.PortfolioAccountService;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class OrderService implements PlaceOrderUseCase, CancelOrderUseCase {

    private final PortfolioAccountService portfolioAccountService;
    private final OrderRepository orderRepository;
    private final OrderValidator orderValidator;
    private final OrderReservationStrategyRegistry reservationStrategies;
    private final OrderFactory orderFactory;

    @Override
    public Order placeOrder(UUID userId, String symbol, String type, Integer quantity) {
        return placeOrder(userId, symbol, type, quantity, OrderConstants.DEFAULT_ORDER_PRICE);
    }

    @Override
    @Transactional
    public Order placeOrder(UUID userId, String symbol, String type, Integer quantity, BigDecimal price) {
        ValidatedOrderRequest request = orderValidator.validate(userId, symbol, type, quantity, price);
        Portfolio portfolio = portfolioAccountService.getOrCreate(userId);
        OrderReservationStrategy strategy = reservationStrategies.get(request.type());

        strategy.reserve(portfolio, request);

        return orderRepository.save(orderFactory.pendingOrder(request, portfolio));
    }

    @Override
    @Transactional
    public Order cancelOrder(UUID orderId, Optional<UUID> userId) {
        if (orderId == null) {
            throw new BadRequestException("orderId is required");
        }

        Order order = userId
                .map(uid -> orderRepository.findByIdAndUserId(orderId, uid))
                .orElseGet(() -> orderRepository.findById(orderId))
                .orElseThrow(() -> new NotFoundException("Order not found"));

        if (!OrderConstants.PENDING.equals(order.getStatus())) {
            throw new ConflictException("Only PENDING orders can be cancelled");
        }

        reservationStrategies.get(order.getType()).release(order);

        order.setStatus(OrderConstants.CANCELLED);
        order.setCancelledAt(java.time.LocalDateTime.now());
        return orderRepository.save(order);
    }
}
