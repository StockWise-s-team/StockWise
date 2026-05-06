package com.stockwise.portfolio.domain.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "transactions")
@Data
public class Transaction {
    @Id
    @GeneratedValue
    private UUID id;

    private UUID portfolioId;

    private String symbol;

    private String type;

    private BigDecimal price;

    private Integer quantity;

    private LocalDateTime executedAt;
}
