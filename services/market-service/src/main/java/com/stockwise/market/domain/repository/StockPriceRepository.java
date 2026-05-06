package com.stockwise.market.domain.repository;

import com.stockwise.market.domain.entity.StockPrice;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;

public interface StockPriceRepository extends JpaRepository<StockPrice, Long> {
    List<StockPrice> findBySymbolAndTradeDateBetween(String symbol, LocalDate start, LocalDate end);
}
