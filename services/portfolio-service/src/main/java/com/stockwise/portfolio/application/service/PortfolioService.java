package com.stockwise.portfolio.application.service;

import com.stockwise.portfolio.application.port.in.GetPnLUseCase;
import com.stockwise.portfolio.application.port.in.GetPortfolioUseCase;
import com.stockwise.portfolio.application.port.in.PlaceOrderUseCase;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class PortfolioService implements GetPortfolioUseCase, PlaceOrderUseCase, GetPnLUseCase {

    @Override
    public Portfolio getPortfolio(UUID userId) {
        Portfolio portfolio = new Portfolio();
        portfolio.setId(UUID.randomUUID());
        portfolio.setUserId(userId);
        portfolio.setVirtualCash(new BigDecimal("100000000"));
        return portfolio;
    }

    @Override
    public List<Holding> getHoldings(UUID portfolioId) {
        Holding holding = new Holding();
        holding.setId(UUID.randomUUID());
        holding.setPortfolioId(portfolioId);
        holding.setSymbol("AAPL");
        holding.setQuantity(100);
        holding.setAvgPrice(new BigDecimal("150.00"));
        return List.of(holding);
    }

    @Override
    public List<Transaction> getTransactionHistory(UUID portfolioId) {
        Transaction tx = new Transaction();
        tx.setId(UUID.randomUUID());
        tx.setPortfolioId(portfolioId);
        tx.setSymbol("AAPL");
        tx.setType("BUY");
        tx.setPrice(new BigDecimal("150.00"));
        tx.setQuantity(100);
        tx.setExecutedAt(LocalDateTime.now());
        return List.of(tx);
    }

    @Override
    public Transaction placeOrder(UUID userId, String symbol, String type, Integer quantity) {
        return placeOrder(userId, symbol, type, quantity, new BigDecimal("150.00"));
    }

    @Override
    public Transaction placeOrder(UUID userId, String symbol, String type, Integer quantity, BigDecimal price) {
        Transaction tx = new Transaction();
        tx.setId(UUID.randomUUID());
        tx.setPortfolioId(UUID.randomUUID());
        tx.setSymbol(symbol);
        tx.setType(type.toUpperCase());
        tx.setPrice(price);
        tx.setQuantity(quantity);
        tx.setExecutedAt(LocalDateTime.now());
        return tx;
    }

    @Override
    public BigDecimal getTotalPnl(UUID userId) {
        return new BigDecimal("500.00");
    }
}
