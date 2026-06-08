package com.stockwise.portfolio.adapter.out.messaging;

import com.stockwise.portfolio.application.port.out.PortfolioEventPublisher;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.core.AmqpTemplate;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * RabbitMQ adapter implementing the PortfolioEventPublisher output port.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RabbitPortfolioEventPublisher implements PortfolioEventPublisher {

    private final AmqpTemplate rabbitTemplate;

    public record PortfolioUpdatedEvent(
            UUID portfolioId,
            UUID userId,
            String symbol,
            String transactionType,
            Integer quantity,
            BigDecimal price,
            LocalDateTime timestamp
    ) {}

    @Override
    public void publishPortfolioUpdated(Portfolio portfolio, Order order, BigDecimal matchPrice) {
        try {
            PortfolioUpdatedEvent event = new PortfolioUpdatedEvent(
                    portfolio.getId(),
                    portfolio.getUserId(),
                    order.getSymbol(),
                    order.getType(),
                    order.getQuantity(),
                    matchPrice,
                    LocalDateTime.now()
            );
            log.info("Publishing portfolio updated event to portfolio.exchange: {}", event);
            rabbitTemplate.convertAndSend("portfolio.exchange", "updated", event);
        } catch (Exception e) {
            log.error("Failed to publish portfolio updated event to RabbitMQ: {}", e.getMessage(), e);
        }
    }
}
