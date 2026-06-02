package com.stockwise.portfolio.application.service.order;

import com.stockwise.portfolio.application.exception.ConflictException;
import com.stockwise.portfolio.application.service.PortfolioAccountService;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import com.stockwise.portfolio.domain.repository.OrderRepository;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private PortfolioRepository portfolioRepository;

    @Mock
    private HoldingRepository holdingRepository;

    @Mock
    private OrderRepository orderRepository;

    private OrderService orderService;

    @BeforeEach
    void setUp() {
        PortfolioAccountService portfolioAccountService = new PortfolioAccountService(portfolioRepository);
        OrderReservationStrategyRegistry reservationStrategies = new OrderReservationStrategyRegistry(List.of(
                new BuyOrderReservationStrategy(portfolioRepository),
                new SellOrderReservationStrategy(holdingRepository)
        ));
        orderService = new OrderService(
                portfolioAccountService,
                orderRepository,
                new DefaultOrderValidator(),
                reservationStrategies,
                new OrderFactory()
        );
    }

    @Test
    void placeBuyOrderFreezesCashAndCreatesPendingOrder() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("1000.00"));
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Order order = orderService.placeOrder(userId, " fpt ", "buy", 2, new BigDecimal("100.00"));

        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("800.00");
        assertThat(order.getSymbol()).isEqualTo("FPT");
        assertThat(order.getType()).isEqualTo(OrderConstants.BUY);
        assertThat(order.getStatus()).isEqualTo(OrderConstants.PENDING);
        assertThat(order.getPrice()).isEqualByComparingTo("100.00");
        verify(portfolioRepository).save(portfolio);
    }

    @Test
    void placeSellOrderFreezesHoldingAndCreatesPendingOrder() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("1000.00"));
        Holding holding = holding(portfolio.getId(), "FPT", 10);
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));
        when(holdingRepository.findByPortfolioIdAndSymbol(portfolio.getId(), "FPT")).thenReturn(Optional.of(holding));
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Order order = orderService.placeOrder(userId, "FPT", "SELL", 4, new BigDecimal("100.00"));

        assertThat(holding.getQuantity()).isEqualTo(6);
        assertThat(order.getType()).isEqualTo(OrderConstants.SELL);
        assertThat(order.getStatus()).isEqualTo(OrderConstants.PENDING);
        verify(holdingRepository).save(holding);
    }

    @Test
    void cancelPendingBuyOrderUnfreezesCash() {
        UUID userId = UUID.randomUUID();
        UUID orderId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("800.00"));
        Order order = order(orderId, userId, portfolio.getId(), OrderConstants.BUY, 2, new BigDecimal("100.00"), OrderConstants.PENDING);
        when(orderRepository.findByIdAndUserId(orderId, userId)).thenReturn(Optional.of(order));
        when(portfolioRepository.findById(portfolio.getId())).thenReturn(Optional.of(portfolio));
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Order cancelled = orderService.cancelOrder(orderId, Optional.of(userId));

        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("1000.00");
        assertThat(cancelled.getStatus()).isEqualTo(OrderConstants.CANCELLED);
        assertThat(cancelled.getCancelledAt()).isNotNull();
    }

    @Test
    void cancelRejectsNonPendingOrder() {
        UUID userId = UUID.randomUUID();
        UUID orderId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("800.00"));
        Order order = order(orderId, userId, portfolio.getId(), OrderConstants.BUY, 2, new BigDecimal("100.00"), "FILLED");
        when(orderRepository.findByIdAndUserId(orderId, userId)).thenReturn(Optional.of(order));

        assertThatThrownBy(() -> orderService.cancelOrder(orderId, Optional.of(userId)))
                .isInstanceOf(ConflictException.class)
                .hasMessage("Only PENDING orders can be cancelled");
    }

    @Test
    void placeOrderRejectsUnsupportedTypeWithoutChangingAssets() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("1000.00"));
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));

        assertThatThrownBy(() -> orderService.placeOrder(userId, "FPT", "SHORT", 1, new BigDecimal("100.00")))
                .isInstanceOf(com.stockwise.portfolio.application.exception.BadRequestException.class)
                .hasMessage("Unsupported order type: SHORT");

        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("1000.00");
    }

    private Portfolio portfolio(UUID userId, BigDecimal cash) {
        Portfolio portfolio = new Portfolio();
        portfolio.setId(UUID.randomUUID());
        portfolio.setUserId(userId);
        portfolio.setVirtualCash(cash);
        return portfolio;
    }

    private Holding holding(UUID portfolioId, String symbol, int quantity) {
        Holding holding = new Holding();
        holding.setId(UUID.randomUUID());
        holding.setPortfolioId(portfolioId);
        holding.setSymbol(symbol);
        holding.setQuantity(quantity);
        holding.setAvgPrice(new BigDecimal("100.00"));
        return holding;
    }

    private Order order(UUID orderId, UUID userId, UUID portfolioId, String type, int quantity, BigDecimal price, String status) {
        Order order = new Order();
        order.setId(orderId);
        order.setUserId(userId);
        order.setPortfolioId(portfolioId);
        order.setSymbol("FPT");
        order.setType(type);
        order.setQuantity(quantity);
        order.setPrice(price);
        order.setStatus(status);
        return order;
    }
}
