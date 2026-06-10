package com.stockwise.portfolio.adapter.out.messaging;

import com.stockwise.portfolio.application.port.out.OrderEventPublisher;
import com.stockwise.portfolio.domain.entity.Order;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.core.AmqpTemplate;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * RabbitMQ adapter implementing the OrderEventPublisher output port.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RabbitOrderEventPublisher implements OrderEventPublisher {

    private final AmqpTemplate rabbitTemplate;

    public record OrderEventPayload(
            UUID orderId,
            UUID userId,
            UUID portfolioId,
            String symbol,
            String type,
            BigDecimal price,
            Integer quantity,
            String status,
            LocalDateTime timestamp
    ) {}

    @Override
    public void publishOrderCreated(Order order) {
        publishOrderEvent("order.created", order);
    }

    @Override
    public void publishOrderCancelled(Order order) {
        publishOrderEvent("order.cancelled", order);
    }

    private void publishOrderEvent(String routingKey, Order order) {
        try {
            OrderEventPayload payload = new OrderEventPayload(
                    order.getId(),
                    order.getUserId(),
                    order.getPortfolioId(),
                    order.getSymbol(),
                    order.getType(),
                    order.getPrice(),
                    order.getQuantity(),
                    order.getStatus(),
                    order.getCreatedAt() != null ? order.getCreatedAt() : LocalDateTime.now()
            );
            log.info("Publishing order event to order.exchange with routing key {}: {}", routingKey, payload);
            rabbitTemplate.convertAndSend("order.exchange", routingKey, payload);
        } catch (Exception e) {
            log.error("Failed to publish order event to RabbitMQ: {}", e.getMessage(), e);
        }
    }
}
