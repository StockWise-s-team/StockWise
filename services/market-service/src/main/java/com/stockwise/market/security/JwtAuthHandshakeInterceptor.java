package com.stockwise.market.security;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.HandshakeInterceptor;

import java.util.Map;

@Component
public class JwtAuthHandshakeInterceptor implements HandshakeInterceptor {

    private static final Logger log = LoggerFactory.getLogger(JwtAuthHandshakeInterceptor.class);
    private final JwtTokenProvider jwtTokenProvider;

    public JwtAuthHandshakeInterceptor(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Override
    public boolean beforeHandshake(
            ServerHttpRequest request,
            ServerHttpResponse response,
            WebSocketHandler wsHandler,
            Map<String, Object> attributes) {

        String token = extractToken(request);
        if (token == null || !jwtTokenProvider.validateToken(token)) {
            log.warn("WebSocket handshake rejected: invalid or missing token");
            return false;
        }

        String tokenType = jwtTokenProvider.getTokenType(token);
        if (!"access".equals(tokenType)) {
            log.warn("WebSocket handshake rejected: token type is '{}', expected 'access'", tokenType);
            return false;
        }

        attributes.put("userId", jwtTokenProvider.getUserIdFromToken(token));
        attributes.put("role", jwtTokenProvider.getRoleFromToken(token));
        attributes.put("token", token);
        log.debug("WebSocket handshake accepted for user {}", attributes.get("userId"));
        return true;
    }

    @Override
    public void afterHandshake(
            ServerHttpRequest request,
            ServerHttpResponse response,
            WebSocketHandler wsHandler,
            Exception exception) {
    }

    private String extractToken(ServerHttpRequest request) {
        String query = request.getURI().getQuery();
        if (query == null) {
            return null;
        }
        for (String param : query.split("&")) {
            String[] kv = param.split("=", 2);
            if (kv.length == 2 && "token".equals(kv[0])) {
                return kv[1];
            }
        }
        return null;
    }
}
