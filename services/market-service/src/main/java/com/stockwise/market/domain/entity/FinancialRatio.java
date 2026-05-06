package com.stockwise.market.domain.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

import java.math.BigDecimal;

@Entity
@Table(name = "financial_ratios")
@Data
public class FinancialRatio {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;

    private String period;

    private BigDecimal peRatio;

    private BigDecimal pbRatio;

    private BigDecimal eps;

    private BigDecimal roe;

    private BigDecimal roa;
}
