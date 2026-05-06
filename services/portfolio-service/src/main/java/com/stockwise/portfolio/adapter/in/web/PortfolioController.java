package com.stockwise.portfolio.adapter.in.web;

import com.stockwise.portfolio.application.port.in.GetPnLUseCase;
import com.stockwise.portfolio.application.port.in.GetPortfolioUseCase;
import com.stockwise.portfolio.application.port.in.PlaceOrderUseCase;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/portfolio")
@RequiredArgsConstructor
public class PortfolioController {

    private final GetPortfolioUseCase getPortfolioUseCase;
    private final PlaceOrderUseCase placeOrderUseCase;
    private final GetPnLUseCase getPnLUseCase;

    @GetMapping
    public ResponseEntity<Map<String, Object>> getPortfolio(@RequestParam String userId) {
        UUID uid = UUID.fromString(userId);
        Portfolio portfolio = getPortfolioUseCase.getPortfolio(uid);
        List<Holding> holdings = getPortfolioUseCase.getHoldings(portfolio.getId());
        List<Transaction> transactions = getPortfolioUseCase.getTransactionHistory(portfolio.getId());
        return ResponseEntity.ok(Map.of(
                "portfolio", portfolio,
                "holdings", holdings,
                "transactions", transactions
        ));
    }

    @PostMapping("/order")
    public ResponseEntity<Transaction> placeOrder(@RequestBody Map<String, Object> orderRequest) {
        UUID userId = UUID.fromString((String) orderRequest.get("userId"));
        String symbol = (String) orderRequest.get("symbol");
        String type = (String) orderRequest.get("type");
        Integer quantity = (Integer) orderRequest.get("quantity");
        BigDecimal price = orderRequest.containsKey("price")
                ? new BigDecimal(orderRequest.get("price").toString())
                : new BigDecimal("150.00");
        return ResponseEntity.ok(placeOrderUseCase.placeOrder(userId, symbol, type, quantity, price));
    }

    @GetMapping("/pnl")
    public ResponseEntity<Map<String, BigDecimal>> getPnl(@RequestParam String userId) {
        UUID uid = UUID.fromString(userId);
        BigDecimal pnl = getPnLUseCase.getTotalPnl(uid);
        return ResponseEntity.ok(Map.of("totalPnl", pnl));
    }
}
