package com.stockwise.portfolio.domain.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "holdings")
@Data
public class Holding {
    @Id
    @GeneratedValue
    private UUID id;

    private UUID portfolioId;

    private String symbol;

    private Integer quantity;

    private BigDecimal avgPrice;
}
