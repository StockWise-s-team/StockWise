package com.stockwise.portfolio.application.service.order;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockwise.portfolio.application.service.order.validation.InMemorySymbolPriceCache;
import com.stockwise.portfolio.application.service.order.validation.SymbolPriceCache;
import com.stockwise.portfolio.application.port.out.PortfolioEventPublisher;
import com.stockwise.portfolio.domain.entity.Holding;
import com.stockwise.portfolio.domain.entity.Order;
import com.stockwise.portfolio.domain.entity.Portfolio;
import com.stockwise.portfolio.domain.repository.HoldingRepository;
import com.stockwise.portfolio.domain.repository.OrderRepository;
import com.stockwise.portfolio.domain.repository.PortfolioRepository;
import com.stockwise.portfolio.domain.repository.TransactionRepository;
import com.stockwise.portfolio.messaging.PriceUpdateListener;
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
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PriceUpdateListenerAndMatchTest {

    private SymbolPriceCache symbolPriceCache;

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PortfolioRepository portfolioRepository;

    @Mock
    private HoldingRepository holdingRepository;

    @Mock
    private TransactionRepository transactionRepository;

    @Mock
    private PortfolioEventPublisher portfolioEventPublisher;

    private PriceUpdateListener priceUpdateListener;
    private OrderMatchProcessor orderMatchProcessor;

    @BeforeEach
    void setUp() {
        symbolPriceCache = new InMemorySymbolPriceCache();
        
        com.stockwise.portfolio.application.service.order.match.OrderMatchStrategyRegistry registry = 
                new com.stockwise.portfolio.application.service.order.match.OrderMatchStrategyRegistry(List.of(
                        new com.stockwise.portfolio.application.service.order.match.BuyOrderMatchStrategy(portfolioRepository, holdingRepository),
                        new com.stockwise.portfolio.application.service.order.match.SellOrderMatchStrategy(portfolioRepository, holdingRepository)
                ));
        
        orderMatchProcessor = new OrderMatchProcessor(
                orderRepository,
                portfolioRepository,
                transactionRepository,
                registry,
                portfolioEventPublisher
        );
        priceUpdateListener = new PriceUpdateListener(
                new ObjectMapper(),
                symbolPriceCache,
                orderMatchProcessor
        );
    }

    @Test
    void priceUpdateEventUpdatesCacheAndMatchesPendingBuyOrder() {
        String jsonMessage = "{\"symbol\":\"FPT\",\"price\":\"100.00\"}";
        
        UUID portfolioId = UUID.randomUUID();
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = new Portfolio();
        portfolio.setId(portfolioId);
        portfolio.setUserId(userId);
        portfolio.setVirtualCash(new BigDecimal("1000.00")); // cash already deducted on reserve
        
        Order buyOrder = new Order();
        buyOrder.setId(UUID.randomUUID());
        buyOrder.setUserId(userId);
        buyOrder.setPortfolioId(portfolioId);
        buyOrder.setSymbol("FPT");
        buyOrder.setType(OrderConstants.BUY);
        buyOrder.setPrice(new BigDecimal("105.00")); // 105.00 >= 100.00 -> should match!
        buyOrder.setQuantity(2);
        buyOrder.setStatus(OrderConstants.PENDING);

        when(orderRepository.findBySymbolAndStatus("FPT", OrderConstants.PENDING)).thenReturn(List.of(buyOrder));
        when(portfolioRepository.findById(portfolioId)).thenReturn(Optional.of(portfolio));
        when(holdingRepository.findByPortfolioIdAndSymbol(portfolioId, "FPT")).thenReturn(Optional.empty());

        // Trigger listener
        priceUpdateListener.onPriceUpdate(jsonMessage);

        // Verify symbol price was saved in local in-memory cache
        assertThat(symbolPriceCache.get("FPT")).isPresent();
        assertThat(symbolPriceCache.get("FPT").get().price()).isEqualByComparingTo("100.00");

        // Verify buy match logic:
        // refund cash = (105 - 100) * 2 = 10.00. Cash becomes 1000 + 10 = 1010
        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("1010.00");
        verify(portfolioRepository).save(portfolio);

        // Verify holding was created/saved
        verify(holdingRepository).save(any(Holding.class));

        // Verify order status updated to FILLED and transaction appended
        assertThat(buyOrder.getStatus()).isEqualTo("FILLED");
        verify(orderRepository).save(buyOrder);
        verify(transactionRepository).save(any(com.stockwise.portfolio.domain.entity.Transaction.class));

        // Verify portfolio.updated event was published
        verify(portfolioEventPublisher).publishPortfolioUpdated(eq(portfolio), eq(buyOrder), eq(new BigDecimal("100.00")));
    }

    @Test
    void priceUpdateEventUpdatesCacheAndMatchesPendingSellOrder() {
        String jsonMessage = "{\"symbol\":\"FPT\",\"close\":\"100.00\"}"; // use close key this time
        
        UUID portfolioId = UUID.randomUUID();
        UUID userId = UUID.randomUUID();
        Portfolio portfolio = new Portfolio();
        portfolio.setId(portfolioId);
        portfolio.setUserId(userId);
        portfolio.setVirtualCash(new BigDecimal("1000.00"));
        
        Order sellOrder = new Order();
        sellOrder.setId(UUID.randomUUID());
        sellOrder.setUserId(userId);
        sellOrder.setPortfolioId(portfolioId);
        sellOrder.setSymbol("FPT");
        sellOrder.setType(OrderConstants.SELL);
        sellOrder.setPrice(new BigDecimal("95.00")); // 95.00 <= 100.00 -> should match!
        sellOrder.setQuantity(4);
        sellOrder.setStatus(OrderConstants.PENDING);

        Holding holding = new Holding();
        holding.setPortfolioId(portfolioId);
        holding.setSymbol("FPT");
        holding.setQuantity(0); // already deducted on reserve

        when(orderRepository.findBySymbolAndStatus("FPT", OrderConstants.PENDING)).thenReturn(List.of(sellOrder));
        when(portfolioRepository.findById(portfolioId)).thenReturn(Optional.of(portfolio));
        when(holdingRepository.findByPortfolioIdAndSymbol(portfolioId, "FPT")).thenReturn(Optional.of(holding));

        // Trigger listener
        priceUpdateListener.onPriceUpdate(jsonMessage);

        // Verify symbol price was saved in local in-memory cache
        assertThat(symbolPriceCache.get("FPT")).isPresent();
        assertThat(symbolPriceCache.get("FPT").get().price()).isEqualByComparingTo("100.00");

        // Verify sell match logic:
        // cash proceeds = 100.00 * 4 = 400.00. Cash becomes 1000 + 400 = 1400
        assertThat(portfolio.getVirtualCash()).isEqualByComparingTo("1400.00");
        verify(portfolioRepository).save(portfolio);

        // Verify empty holding deleted
        verify(holdingRepository).delete(holding);

        // Verify order status updated to FILLED and transaction appended
        assertThat(sellOrder.getStatus()).isEqualTo("FILLED");
        verify(orderRepository).save(sellOrder);
        verify(transactionRepository).save(any(com.stockwise.portfolio.domain.entity.Transaction.class));

        // Verify portfolio.updated event was published
        verify(portfolioEventPublisher).publishPortfolioUpdated(eq(portfolio), eq(sellOrder), eq(new BigDecimal("100.00")));
    }
}
