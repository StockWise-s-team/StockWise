package com.stockwise.portfolio.application.service.order.lifecycle;

import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.application.service.order.reservation.OrderReservationStrategyRegistry;
import com.stockwise.portfolio.application.exception.BadRequestException;
import com.stockwise.portfolio.application.exception.ConflictException;
import com.stockwise.portfolio.application.exception.NotFoundException;
import com.stockwise.portfolio.application.port.in.CancelOrderUseCase;
import com.stockwise.portfolio.application.port.out.OrderEventPublisher;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

/**
 * Service implementation for cancelling orders.
 * Adheres to SOLID design principles by delegating balance releasing and event publishing
 * to specialized components.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CancelOrderService implements CancelOrderUseCase {

    private final OrderRepository orderRepository;
    private final OrderReservationStrategyRegistry reservationStrategies;
    private final OrderEventPublisher orderEventPublisher;

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
        order.setCancelledAt(LocalDateTime.now());
        Order savedOrder = orderRepository.save(order);
        orderEventPublisher.publishOrderCancelled(savedOrder);
        return savedOrder;
    }
}
