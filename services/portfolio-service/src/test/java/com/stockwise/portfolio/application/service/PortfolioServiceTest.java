package com.stockwise.portfolio.application.service;

import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import com.stockwise.portfolio.domain.repository.TransactionRepository;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class PortfolioServiceTest {

    private final PortfolioRepository portfolioRepository = mock(PortfolioRepository.class);
    private final HoldingRepository holdingRepository = mock(HoldingRepository.class);
    private final TransactionRepository transactionRepository = mock(TransactionRepository.class);
    private final PortfolioAccountService portfolioAccountService = new PortfolioAccountService(portfolioRepository);
    private final PortfolioService portfolioService = new PortfolioService(
            portfolioAccountService,
            holdingRepository,
            transactionRepository);

    @Test
    void getTotalPnlReturnsZeroAfterBuyOnly() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId);
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));
        when(transactionRepository.findByPortfolioIdOrderByExecutedAtDesc(portfolio.getId())).thenReturn(List.of(
                transaction(portfolio.getId(), OrderConstants.BUY, "FPT", "150.00", 2, 1)
        ));

        assertThat(portfolioService.getTotalPnl(userId)).isEqualByComparingTo("0.00");
    }

    @Test
    void getTotalPnlUsesAverageCostForRealizedSellProfit() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId);
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));
        when(transactionRepository.findByPortfolioIdOrderByExecutedAtDesc(portfolio.getId())).thenReturn(List.of(
                transaction(portfolio.getId(), OrderConstants.SELL, "FPT", "160.00", 2, 3),
                transaction(portfolio.getId(), OrderConstants.BUY, "FPT", "120.00", 1, 2),
                transaction(portfolio.getId(), OrderConstants.BUY, "FPT", "100.00", 3, 1)
        ));

        assertThat(portfolioService.getTotalPnl(userId)).isEqualByComparingTo("110.00");
    }

    private Portfolio portfolio(UUID userId) {
        Portfolio portfolio = new Portfolio();
        portfolio.setId(UUID.randomUUID());
        portfolio.setUserId(userId);
        portfolio.setVirtualCash(new BigDecimal("1000.00"));
        return portfolio;
    }

    private Transaction transaction(UUID portfolioId, String type, String symbol, String price, int quantity, int day) {
        Transaction transaction = new Transaction();
        transaction.setId(UUID.randomUUID());
        transaction.setPortfolioId(portfolioId);
        transaction.setType(type);
        transaction.setSymbol(symbol);
        transaction.setPrice(new BigDecimal(price));
        transaction.setQuantity(quantity);
        transaction.setExecutedAt(LocalDateTime.of(2026, 6, day, 10, 0));
        return transaction;
    }
}
