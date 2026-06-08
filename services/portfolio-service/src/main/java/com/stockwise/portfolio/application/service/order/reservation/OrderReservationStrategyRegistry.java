package com.stockwise.portfolio.application.service.order.reservation;

import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Registry mapping order types (BUY/SELL) to their corresponding OrderReservationStrategy.
 * Supports the Open/Closed Principle (OCP) by automatically resolving Spring-managed strategy beans.
 */
@Component
public class OrderReservationStrategyRegistry {

    private final Map<String, OrderReservationStrategy> strategiesByType;

    public OrderReservationStrategyRegistry(List<OrderReservationStrategy> strategies) {
        this.strategiesByType = strategies.stream()
                .collect(Collectors.toUnmodifiableMap(OrderReservationStrategy::orderType, Function.identity()));
    }

    /**
     * Resolves the reservation strategy for a given order type.
     * Throws a BadRequestException if the order type is not supported.
     *
     * @param type the order type string (BUY/SELL)
     * @return the resolved reservation strategy
     */
    public OrderReservationStrategy get(String type) {
        OrderReservationStrategy strategy = strategiesByType.get(type);
        if (strategy == null) {
            throw new BadRequestException("Unsupported order type: " + type);
        }
        return strategy;
    }
}
