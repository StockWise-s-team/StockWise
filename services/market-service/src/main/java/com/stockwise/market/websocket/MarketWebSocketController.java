package com.stockwise.market.websocket;

import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.messaging.MarketDataConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.stereotype.Controller;

@Controller
public class MarketWebSocketController {

    private static final Logger log = LoggerFactory.getLogger(MarketWebSocketController.class);

    private final WebSocketSessionRegistry sessionRegistry;
    private final MarketDataConsumer marketDataConsumer;

    public MarketWebSocketController(WebSocketSessionRegistry sessionRegistry,
                                    MarketDataConsumer marketDataConsumer) {
        this.sessionRegistry = sessionRegistry;
        this.marketDataConsumer = marketDataConsumer;
    }

    @MessageMapping("/subscribe/{symbol}")
    @SendTo("/topic/price/{symbol}")
    public LatestPriceResponse subscribe(
            @DestinationVariable String symbol,
            StompHeaderAccessor stomp) {
        String sessionId = stomp.getSessionId();
        sessionRegistry.onSubscribe(stomp, sessionId);

        LatestPriceResponse cached = marketDataConsumer.getCachedPrice(symbol);
        if (cached != null) {
            log.debug("Sending cached price for {} to newly subscribed session {}", symbol, sessionId);
            return cached;
        }
        return null;
    }

    @MessageMapping("/unsubscribe/{symbol}")
    public void unsubscribe(
            @DestinationVariable String symbol,
            StompHeaderAccessor stomp) {
        String sessionId = stomp.getSessionId();
        sessionRegistry.onUnsubscribe(stomp, sessionId);
    }
}
