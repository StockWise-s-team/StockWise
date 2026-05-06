package com.stockwise.portfolio.application.port.in;

import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Transaction;

import java.util.List;
import java.util.Map;
import java.util.UUID;

public interface GetPortfolioUseCase {
    Portfolio getPortfolio(UUID userId);
    List<Holding> getHoldings(UUID portfolioId);
    List<Transaction> getTransactionHistory(UUID portfolioId);
}
