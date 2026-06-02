package com.stockwise.portfolio.application.service.order;

import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@Component
public class OrderReservationStrategyRegistry {

    private final Map<String, OrderReservationStrategy> strategiesByType;

    public OrderReservationStrategyRegistry(List<OrderReservationStrategy> strategies) {
        this.strategiesByType = strategies.stream()
                .collect(Collectors.toUnmodifiableMap(OrderReservationStrategy::orderType, Function.identity()));
    }

    public OrderReservationStrategy get(String type) {
        OrderReservationStrategy strategy = strategiesByType.get(type);
        if (strategy == null) {
            throw new BadRequestException("Unsupported order type: " + type);
        }
        return strategy;
    }
}
