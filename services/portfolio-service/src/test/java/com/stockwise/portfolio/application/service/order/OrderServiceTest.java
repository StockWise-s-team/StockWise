package com.stockwise.portfolio.application.service.order;

import com.stockwise.portfolio.application.service.order.lifecycle.CancelOrderService;
import com.stockwise.portfolio.application.service.order.lifecycle.OrderFactory;
import com.stockwise.portfolio.application.service.order.lifecycle.PlaceOrderService;
import com.stockwise.portfolio.application.service.order.reservation.BuyOrderReservationStrategy;
import com.stockwise.portfolio.application.service.order.reservation.OrderReservationStrategyRegistry;
import com.stockwise.portfolio.application.service.order.reservation.SellOrderReservationStrategy;
import com.stockwise.portfolio.application.exception.ConflictException;
import com.stockwise.portfolio.application.port.out.OrderEventPublisher;
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

    private com.stockwise.portfolio.application.service.order.validation.SymbolPriceCache symbolPriceCache;

    @Mock
    private OrderEventPublisher orderEventPublisher;

    private PlaceOrderService placeOrderService;
    private CancelOrderService cancelOrderService;

    @BeforeEach
    void setUp() {
        symbolPriceCache = new com.stockwise.portfolio.application.service.order.validation.InMemorySymbolPriceCache();
        PortfolioAccountService portfolioAccountService = new PortfolioAccountService(portfolioRepository);
        OrderReservationStrategyRegistry reservationStrategies = new OrderReservationStrategyRegistry(List.of(
                new BuyOrderReservationStrategy(portfolioRepository),
                new SellOrderReservationStrategy(holdingRepository)
        ));
        
        com.stockwise.portfolio.application.service.order.validation.DefaultOrderValidator validator =
                new com.stockwise.portfolio.application.service.order.validation.DefaultOrderValidator(List.of(
                        new com.stockwise.portfolio.application.service.order.validation.BasicFormatValidationRule(),
                        new com.stockwise.portfolio.application.service.order.validation.TradingHoursValidationRule(false, java.time.Clock.systemDefaultZone()),
                        new com.stockwise.portfolio.application.service.order.validation.PriceBandValidationRule(symbolPriceCache, false)
                ), symbolPriceCache, orderRepository);
                
        placeOrderService = new PlaceOrderService(
                portfolioAccountService,
                orderRepository,
                validator,
                reservationStrategies,
                new OrderFactory(),
                orderEventPublisher
        );

        cancelOrderService = new CancelOrderService(
                orderRepository,
                reservationStrategies,
                orderEventPublisher
        );
    }

    @Test
    void placeBuyOrderFreezesCashAndCreatesPendingOrder() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("1000.00"));
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Order order = placeOrderService.placeOrder(userId, " fpt ", "buy", 2, new BigDecimal("100.00"));

        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("800.00");
        assertThat(order.getSymbol()).isEqualTo("FPT");
        assertThat(order.getType()).isEqualTo(OrderConstants.BUY);
        assertThat(order.getStatus()).isEqualTo(OrderConstants.PENDING);
        assertThat(order.getPrice()).isEqualByComparingTo("100.00");
        verify(portfolioRepository).save(portfolio);
        verify(orderEventPublisher).publishOrderCreated(any(Order.class));
    }

    @Test
    void placeSellOrderFreezesHoldingAndCreatesPendingOrder() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("1000.00"));
        Holding holding = holding(portfolio.getId(), "FPT", 10);
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));
        when(holdingRepository.findByPortfolioIdAndSymbol(portfolio.getId(), "FPT")).thenReturn(Optional.of(holding));
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Order order = placeOrderService.placeOrder(userId, "FPT", "SELL", 4, new BigDecimal("100.00"));

        assertThat(holding.getQuantity()).isEqualTo(6);
        assertThat(order.getType()).isEqualTo(OrderConstants.SELL);
        assertThat(order.getStatus()).isEqualTo(OrderConstants.PENDING);
        verify(holdingRepository).save(holding);
        verify(orderEventPublisher).publishOrderCreated(any(Order.class));
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

        Order cancelled = cancelOrderService.cancelOrder(orderId, Optional.of(userId));

        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("1000.00");
        assertThat(cancelled.getStatus()).isEqualTo(OrderConstants.CANCELLED);
        assertThat(cancelled.getCancelledAt()).isNotNull();
        verify(orderEventPublisher).publishOrderCancelled(any(Order.class));
    }

    @Test
    void cancelRejectsNonPendingOrder() {
        UUID userId = UUID.randomUUID();
        UUID orderId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("800.00"));
        Order order = order(orderId, userId, portfolio.getId(), OrderConstants.BUY, 2, new BigDecimal("100.00"), "FILLED");
        when(orderRepository.findByIdAndUserId(orderId, userId)).thenReturn(Optional.of(order));

        assertThatThrownBy(() -> cancelOrderService.cancelOrder(orderId, Optional.of(userId)))
                .isInstanceOf(ConflictException.class)
                .hasMessage("Only PENDING orders can be cancelled");
    }

    @Test
    void placeOrderRejectsUnsupportedTypeWithoutChangingAssets() {
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = portfolio(userId, new BigDecimal("1000.00"));
        when(portfolioRepository.findByUserId(userId)).thenReturn(Optional.of(portfolio));

        assertThatThrownBy(() -> placeOrderService.placeOrder(userId, "FPT", "SHORT", 1, new BigDecimal("100.00")))
                .isInstanceOf(com.stockwise.portfolio.application.exception.BadRequestException.class)
                .hasMessage("Unsupported order type: SHORT");

        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("1000.00");
    }

    @Test
    void placeBuyOrderRejectsPriceOutOfCeiling() {
        UUID userId = UUID.randomUUID();
        symbolPriceCache.put("FPT", new BigDecimal("100.00"));

        assertThatThrownBy(() -> placeOrderService.placeOrder(userId, "FPT", "BUY", 1, new BigDecimal("108.00")))
                .isInstanceOf(com.stockwise.portfolio.application.exception.BadRequestException.class)
                .hasMessageContaining("out of the daily price band");
    }

    @Test
    void placeBuyOrderRejectsPriceBelowFloor() {
        UUID userId = UUID.randomUUID();
        symbolPriceCache.put("FPT", new BigDecimal("100.00"));

        assertThatThrownBy(() -> placeOrderService.placeOrder(userId, "FPT", "BUY", 1, new BigDecimal("92.00")))
                .isInstanceOf(com.stockwise.portfolio.application.exception.BadRequestException.class)
                .hasMessageContaining("out of the daily price band");
    }

    @Test
    void placeBuyOrderFailsOutsideTradingHours() {
        UUID userId = UUID.randomUUID();
        PortfolioAccountService portfolioAccountService = new PortfolioAccountService(portfolioRepository);
        OrderReservationStrategyRegistry reservationStrategies = new OrderReservationStrategyRegistry(List.of(
                new BuyOrderReservationStrategy(portfolioRepository),
                new SellOrderReservationStrategy(holdingRepository)
        ));
        
        // Create custom Clock set to a Sunday: 2026-06-07 (Sunday)
        java.time.Instant sundayInstant = java.time.Instant.parse("2026-06-07T10:00:00Z");
        java.time.Clock sundayClock = java.time.Clock.fixed(sundayInstant, java.time.ZoneId.of("UTC"));
        
        com.stockwise.portfolio.application.service.order.validation.DefaultOrderValidator strictValidator =
                new com.stockwise.portfolio.application.service.order.validation.DefaultOrderValidator(List.of(
                        new com.stockwise.portfolio.application.service.order.validation.BasicFormatValidationRule(),
                        new com.stockwise.portfolio.application.service.order.validation.TradingHoursValidationRule(true, sundayClock),
                        new com.stockwise.portfolio.application.service.order.validation.PriceBandValidationRule(symbolPriceCache, true)
                ), symbolPriceCache, orderRepository);

        PlaceOrderService strictPlaceOrderService = new PlaceOrderService(
                portfolioAccountService,
                orderRepository,
                strictValidator,
                reservationStrategies,
                new OrderFactory(),
                orderEventPublisher
        );

        assertThatThrownBy(() -> strictPlaceOrderService.placeOrder(userId, "FPT", "BUY", 1, new BigDecimal("100.00")))
                .isInstanceOf(com.stockwise.portfolio.application.exception.BadRequestException.class)
                .hasMessageContaining("trading days");
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
