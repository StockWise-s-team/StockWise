package com.stockwise.market.websocket;

import com.stockwise.market.adapter.in.web.dto.LatestPriceResponse;
import com.stockwise.market.messaging.MarketDataConsumer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.stereotype.Controller;

@Slf4j
@Controller
@RequiredArgsConstructor
public class MarketWebSocketController {

    private final WebSocketSessionRegistry sessionRegistry;
    private final MarketDataConsumer marketDataConsumer;

    @MessageMapping("/subscribe/{symbol}")
    @SendTo("/topic/price/{symbol}")
    public LatestPriceResponse subscribe(
            @DestinationVariable String symbol,
            SimpMessageHeaderAccessor headerAccessor) {
        StompHeaderAccessor stomp = StompHeaderAccessor.wrap(headerAccessor.getMessage().get());
        String sessionId = stomp.getSessionId();
        sessionRegistry.onSubscribe(stomp, sessionId);

        // Immediately deliver cached price so the client gets instant data
        // instead of waiting for the next pipeline run.
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
            SimpMessageHeaderAccessor headerAccessor) {
        StompHeaderAccessor stomp = StompHeaderAccessor.wrap(headerAccessor.getMessage().get());
        String sessionId = stomp.getSessionId();
        sessionRegistry.onUnsubscribe(stomp, sessionId);
    }
}
