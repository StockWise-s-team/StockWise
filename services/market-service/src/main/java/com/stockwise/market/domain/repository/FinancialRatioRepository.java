package com.stockwise.market.domain.repository;

import com.stockwise.market.domain.entity.FinancialRatio;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface FinancialRatioRepository extends JpaRepository<FinancialRatio, Long> {
    List<FinancialRatio> findBySymbolOrderByPeriodDesc(String symbol);
}
