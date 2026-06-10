package com.stockwise.portfolio.domain.repository;

import com.stockwise.portfolio.domain.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface OrderRepository extends JpaRepository<Order, UUID> {
    Optional<Order> findByIdAndUserId(UUID id, UUID userId);
    List<Order> findBySymbolAndStatus(String symbol, String status);
}
