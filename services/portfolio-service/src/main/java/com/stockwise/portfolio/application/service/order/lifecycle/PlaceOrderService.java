package com.stockwise.portfolio.application.service.order.lifecycle;

import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.application.service.order.ValidatedOrderRequest;
import com.stockwise.portfolio.application.service.order.ports.OrderReservationStrategy;
import com.stockwise.portfolio.application.service.order.reservation.OrderReservationStrategyRegistry;
import com.stockwise.portfolio.application.service.order.ports.OrderValidator;
import com.stockwise.portfolio.application.port.in.PlaceOrderUseCase;
import com.stockwise.portfolio.application.port.out.OrderEventPublisher;
import com.stockwise.portfolio.application.service.PortfolioAccountService;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.UUID;

/**
 * Service implementation for placing orders.
 * Adheres to SOLID design principles by delegating validation, balance reservation,
 * order instantiation, and event publishing to specialized components.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PlaceOrderService implements PlaceOrderUseCase {

    private final PortfolioAccountService portfolioAccountService;
    private final OrderRepository orderRepository;
    private final OrderValidator orderValidator;
    private final OrderReservationStrategyRegistry reservationStrategies;
    private final OrderFactory orderFactory;
    private final OrderEventPublisher orderEventPublisher;

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

        Order savedOrder = orderRepository.save(orderFactory.pendingOrder(request, portfolio));
        orderEventPublisher.publishOrderCreated(savedOrder);
        return savedOrder;
    }
}
