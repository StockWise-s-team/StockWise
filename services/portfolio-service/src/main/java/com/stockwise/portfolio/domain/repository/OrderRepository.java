package com.stockwise.portfolio.domain.repository;

import com.stockwise.portfolio.domain.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface OrderRepository extends JpaRepository<Order, UUID> {
    Optional<Order> findByIdAndUserId(UUID id, UUID userId);
    List<Order> findBySymbolAndStatus(String symbol, String status);

    @Query(value = "SELECT close FROM stock_prices WHERE symbol = :symbol ORDER BY trade_date DESC LIMIT 1", nativeQuery = true)
    BigDecimal findLatestPriceBySymbol(@Param("symbol") String symbol);
}
