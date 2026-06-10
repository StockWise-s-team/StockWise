package com.stockwise.portfolio.adapter.in.web.dto;

import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;

import java.util.List;

public record PortfolioResponse(
        Portfolio portfolio,
        List<Holding> holdings,
        List<Transaction> transactions
) {
}
