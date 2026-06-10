package com.stockwise.portfolio.domain.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "orders")
@Data
public class Order {
    @Id
    @GeneratedValue
    private UUID id;

    private UUID userId;

    private UUID portfolioId;

    private String symbol;

    private String type;

    private BigDecimal price;

    private Integer quantity;

    private String status;

    private LocalDateTime createdAt;

    private LocalDateTime cancelledAt;

    @PrePersist
    void prePersist() {
        if (status == null) {
            status = "PENDING";
        }
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }
}
