package com.stockwise.portfolio.domain.repository;

import com.stockwise.portfolio.domain.entity.Transaction;
import org.springframework.data.repository.Repository;

import java.util.List;
import java.util.UUID;

public interface TransactionRepository extends Repository<Transaction, UUID> {
    Transaction save(Transaction transaction);
    List<Transaction> findByPortfolioIdOrderByExecutedAtDesc(UUID portfolioId);
}
