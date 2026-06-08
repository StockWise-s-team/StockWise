package com.stockwise.market.domain.repository;

import com.stockwise.market.domain.entity.StockPrice;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface StockPriceRepository extends JpaRepository<StockPrice, Long> {
    List<StockPrice> findTop2BySymbolOrderByTradeDateDesc(String symbol);

    Optional<StockPrice> findTopBySymbolOrderByTradeDateDesc(String symbol);

    List<StockPrice> findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(String symbol, LocalDate start, LocalDate end);
}
