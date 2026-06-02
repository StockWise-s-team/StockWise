package com.stockwise.portfolio.application.service;

import com.stockwise.portfolio.application.port.in.GetPnLUseCase;
import com.stockwise.portfolio.application.port.in.GetPortfolioUseCase;
import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import com.stockwise.portfolio.domain.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PortfolioService implements GetPortfolioUseCase, GetPnLUseCase {

    private final PortfolioAccountService portfolioAccountService;
    private final HoldingRepository holdingRepository;
    private final TransactionRepository transactionRepository;

    @Override
    @Transactional
    public Portfolio getPortfolio(UUID userId) {
        return portfolioAccountService.getOrCreate(userId);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Holding> getHoldings(UUID portfolioId) {
        return holdingRepository.findByPortfolioId(portfolioId);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Transaction> getTransactionHistory(UUID portfolioId) {
        return transactionRepository.findByPortfolioIdOrderByExecutedAtDesc(portfolioId);
    }

    @Override
    @Transactional(readOnly = true)
    public BigDecimal getTotalPnl(UUID userId) {
        Portfolio portfolio = portfolioAccountService.getRequired(userId);

        return transactionRepository.findByPortfolioIdOrderByExecutedAtDesc(portfolio.getId()).stream()
                .map(tx -> transactionCashImpact(tx.getType(), tx.getPrice(), tx.getQuantity()))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private BigDecimal transactionCashImpact(String type, BigDecimal price, Integer quantity) {
        BigDecimal value = price.multiply(BigDecimal.valueOf(quantity));
        return OrderConstants.SELL.equals(type) ? value : value.negate();
    }
}
