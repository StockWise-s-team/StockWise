package com.stockwise.market.websocket;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.messaging.SessionDisconnectEvent;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;

@Component
public class WebSocketSessionRegistry {

    private static final Logger log = LoggerFactory.getLogger(WebSocketSessionRegistry.class);

    private final Map<String, Set<String>> symbolToSessions = new ConcurrentHashMap<>();
    private final Map<String, String> sessionToUser = new ConcurrentHashMap<>();

    public void onSubscribe(StompHeaderAccessor accessor, String sessionId) {
        String userId = accessor.getFirstNativeHeader("userId");
        String symbol = accessor.getFirstNativeHeader("symbol");

        if (symbol == null || symbol.isBlank()) {
            log.debug("Subscribe frame without symbol header, session={}", sessionId);
            return;
        }

        symbol = symbol.trim().toUpperCase();

        if (!isValidSymbol(symbol)) {
            log.warn("[WS] Invalid symbol '{}' rejected from session {}", symbol, sessionId);
            return;
        }

        if (userId != null) {
            sessionToUser.put(sessionId, userId);
        }

        symbolToSessions
                .computeIfAbsent(symbol, k -> new CopyOnWriteArraySet<>())
                .add(sessionId);

        log.info("[WS] Session {} subscribed to symbol {} (user={})", sessionId, symbol, userId);
    }

    private boolean isValidSymbol(String symbol) {
        return symbol.length() <= 10 && symbol.matches("^[A-Z0-9._-]+$");
    }

    public void onUnsubscribe(StompHeaderAccessor accessor, String sessionId) {
        String userId = accessor.getFirstNativeHeader("userId");
        String symbol = accessor.getFirstNativeHeader("symbol");

        if (symbol != null && !symbol.isBlank()) {
            symbol = symbol.trim().toUpperCase();
            symbolToSessions.getOrDefault(symbol, Set.of()).remove(sessionId);
            if (symbolToSessions.get(symbol) != null && symbolToSessions.get(symbol).isEmpty()) {
                symbolToSessions.remove(symbol);
            }
            log.info("[WS] Session {} unsubscribed from symbol {} (user={})", sessionId, symbol, userId);
        }
    }

    public void onDisconnect(SessionDisconnectEvent event, String sessionId) {
        String userId = sessionToUser.remove(sessionId);

        symbolToSessions.values().forEach(sessions -> sessions.remove(sessionId));
        symbolToSessions.entrySet().removeIf(e -> e.getValue().isEmpty());

        log.info("[WS] Session {} disconnected (user={})", sessionId, userId);
    }

    public List<String> getSessionsForSymbol(String symbol) {
        Set<String> sessions = symbolToSessions.get(symbol.trim().toUpperCase());
        if (sessions == null) {
            return List.of();
        }
        return List.copyOf(sessions);
    }

    public Set<String> getAllSubscribedSymbols() {
        return Set.copyOf(symbolToSessions.keySet());
    }

    public int getSessionCount() {
        return sessionToUser.size();
    }
}
