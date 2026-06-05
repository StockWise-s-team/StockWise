package com.stockwise.portfolio.application.service.order.match;

import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Registry mapping order types (BUY/SELL) to their corresponding OrderMatchStrategy.
 * Supports the Open/Closed Principle (OCP) by automatically resolving Spring-managed strategy beans.
 */
@Component
public class OrderMatchStrategyRegistry {

    private final Map<String, OrderMatchStrategy> strategiesByType;

    public OrderMatchStrategyRegistry(List<OrderMatchStrategy> strategies) {
        this.strategiesByType = strategies.stream()
                .collect(Collectors.toUnmodifiableMap(OrderMatchStrategy::orderType, Function.identity()));
    }

    /**
     * Resolves the matching strategy for a given order type.
     * Throws a BadRequestException if the order type is not supported.
     *
     * @param type the order type string (BUY/SELL)
     * @return the resolved matching strategy
     */
    public OrderMatchStrategy get(String type) {
        OrderMatchStrategy strategy = strategiesByType.get(type);
        if (strategy == null) {
            throw new BadRequestException("Unsupported order type for matching: " + type);
        }
        return strategy;
    }
}
