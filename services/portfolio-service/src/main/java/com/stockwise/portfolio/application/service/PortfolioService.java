package com.stockwise.portfolio.application.service;

import com.stockwise.portfolio.application.port.in.GetPnLUseCase;
import com.stockwise.portfolio.application.port.in.GetPortfolioUseCase;
import com.stockwise.portfolio.application.service.order.OrderConstants;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import com.stockwise.portfolio.domain.repository.OrderRepository;
import com.stockwise.portfolio.domain.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PortfolioService implements GetPortfolioUseCase, GetPnLUseCase {

    private final PortfolioAccountService portfolioAccountService;
    private final HoldingRepository holdingRepository;
    private final TransactionRepository transactionRepository;
    private final OrderRepository orderRepository;

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
    public List<Order> getOrderHistory(UUID userId) {
        return orderRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    @Override
    @Transactional(readOnly = true)
    public BigDecimal getTotalPnl(UUID userId) {
        Portfolio portfolio = portfolioAccountService.getRequired(userId);
        Map<String, PositionCost> positions = new HashMap<>();
        BigDecimal realizedPnl = BigDecimal.ZERO;

        List<Transaction> transactions = transactionRepository.findByPortfolioIdOrderByExecutedAtDesc(portfolio.getId()).stream()
                .sorted(Comparator.comparing(
                        Transaction::getExecutedAt,
                        Comparator.nullsLast(Comparator.naturalOrder())))
                .toList();

        for (Transaction tx : transactions) {
            String symbol = tx.getSymbol().toUpperCase();
            PositionCost position = positions.computeIfAbsent(symbol, ignored -> new PositionCost());
            if (OrderConstants.BUY.equals(tx.getType())) {
                position.buy(tx.getPrice(), tx.getQuantity());
            } else if (OrderConstants.SELL.equals(tx.getType())) {
                realizedPnl = realizedPnl.add(position.sell(tx.getPrice(), tx.getQuantity()));
            }
        }

        return realizedPnl;
    }

    private static class PositionCost {
        private int quantity;
        private BigDecimal totalCost = BigDecimal.ZERO;

        private void buy(BigDecimal price, int boughtQuantity) {
            quantity += boughtQuantity;
            totalCost = totalCost.add(price.multiply(BigDecimal.valueOf(boughtQuantity)));
        }

        private BigDecimal sell(BigDecimal price, int soldQuantity) {
            if (quantity <= 0) {
                return BigDecimal.ZERO;
            }

            int matchedQuantity = Math.min(quantity, soldQuantity);
            BigDecimal averageCost = totalCost.divide(BigDecimal.valueOf(quantity), 10, RoundingMode.HALF_UP);
            BigDecimal realized = price.subtract(averageCost).multiply(BigDecimal.valueOf(matchedQuantity));
            quantity -= matchedQuantity;
            totalCost = averageCost.multiply(BigDecimal.valueOf(quantity));
            return realized;
        }
    }
}
