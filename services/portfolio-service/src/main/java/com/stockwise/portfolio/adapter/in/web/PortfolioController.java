package com.stockwise.portfolio.adapter.in.web;

import com.stockwise.portfolio.adapter.in.web.dto.OrderResponse;
import com.stockwise.portfolio.adapter.in.web.dto.PlaceOrderRequest;
import com.stockwise.portfolio.adapter.in.web.dto.PnlResponse;
import com.stockwise.portfolio.adapter.in.web.dto.PortfolioResponse;
import com.stockwise.portfolio.application.port.in.CancelOrderUseCase;
import com.stockwise.portfolio.application.port.in.GetPnLUseCase;
import com.stockwise.portfolio.application.port.in.GetPortfolioUseCase;
import com.stockwise.portfolio.application.port.in.PlaceOrderUseCase;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.entity.Transaction;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/portfolio")
@RequiredArgsConstructor
public class PortfolioController {

    private final GetPortfolioUseCase getPortfolioUseCase;
    private final PlaceOrderUseCase placeOrderUseCase;
    private final CancelOrderUseCase cancelOrderUseCase;
    private final GetPnLUseCase getPnLUseCase;
    private final OrderResponseMapper orderResponseMapper;
    private final UserIdResolver userIdResolver;

    @GetMapping
    public ResponseEntity<PortfolioResponse> getPortfolio() {
        UUID userId = userIdResolver.resolveCurrentUserId();
        Portfolio portfolio = getPortfolioUseCase.getPortfolio(userId);
        List<Holding> holdings = getPortfolioUseCase.getHoldings(portfolio.getId());
        List<Transaction> transactions = getPortfolioUseCase.getTransactionHistory(portfolio.getId());
        return ResponseEntity.ok(new PortfolioResponse(portfolio, holdings, transactions));
    }

    @PostMapping("/order")
    public ResponseEntity<OrderResponse> placeOrder(@RequestBody PlaceOrderRequest request) {
        UUID userId = userIdResolver.resolveCurrentUserId();
        Order order = placeOrderUseCase.placeOrder(
                userId,
                request.symbol(),
                request.type(),
                request.quantity(),
                request.price()
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(orderResponseMapper.placed(order));
    }

    @DeleteMapping("/order/{orderId}")
    public ResponseEntity<OrderResponse> cancelOrder(@PathVariable String orderId) {
        UUID userId = userIdResolver.resolveCurrentUserId();
        Order order = cancelOrderUseCase.cancelOrder(UUID.fromString(orderId), Optional.of(userId));
        return ResponseEntity.ok(orderResponseMapper.cancelled(order));
    }

    @GetMapping("/pnl")
    public ResponseEntity<PnlResponse> getPnl() {
        UUID userId = userIdResolver.resolveCurrentUserId();
        BigDecimal pnl = getPnLUseCase.getTotalPnl(userId);
        return ResponseEntity.ok(new PnlResponse(pnl));
    }
}
