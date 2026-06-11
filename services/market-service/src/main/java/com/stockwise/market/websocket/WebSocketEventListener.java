package com.stockwise.market.websocket;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.messaging.WebSocketDisconnectEvent;
import org.springframework.web.socket.messaging.WebSocketEventListener;

@Slf4j
@Component
@RequiredArgsConstructor
public class WebSocketEventListener implements WebSocketEventListener {

    private final WebSocketSessionRegistry sessionRegistry;

    @Override
    @EventListener
    public void handleWebSocketDisconnectListener(WebSocketDisconnectEvent event) {
        String sessionId = event.getSessionId();
        sessionRegistry.onDisconnect(event, sessionId);
    }
}
