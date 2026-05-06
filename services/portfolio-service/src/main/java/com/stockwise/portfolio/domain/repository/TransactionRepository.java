package com.stockwise.portfolio.domain.repository;

import com.stockwise.portfolio.domain.entity.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface TransactionRepository extends JpaRepository<Transaction, UUID> {
    List<Transaction> findByPortfolioIdOrderByExecutedAtDesc(UUID portfolioId);
}
