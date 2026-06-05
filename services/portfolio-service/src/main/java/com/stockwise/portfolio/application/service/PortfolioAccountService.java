package com.stockwise.portfolio.application.service;

import com.stockwise.portfolio.application.exception.BadRequestException;
import com.stockwise.portfolio.application.exception.NotFoundException;
import com.stockwise.order.OrderConstants;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PortfolioAccountService {

    private final PortfolioRepository portfolioRepository;

    public Portfolio getOrCreate(UUID userId) {
        if (userId == null) {
            throw new BadRequestException("userId is required");
        }
        return portfolioRepository.findByUserId(userId)
                .orElseGet(() -> createPortfolio(userId));
    }

    public Portfolio getRequired(UUID userId) {
        if (userId == null) {
            throw new BadRequestException("userId is required");
        }
        return portfolioRepository.findByUserId(userId)
                .orElseThrow(() -> new NotFoundException("Portfolio not found"));
    }

    private Portfolio createPortfolio(UUID userId) {
        Portfolio portfolio = new Portfolio();
        portfolio.setUserId(userId);
        portfolio.setVirtualCash(OrderConstants.INITIAL_CASH);
        return portfolioRepository.save(portfolio);
    }
}
