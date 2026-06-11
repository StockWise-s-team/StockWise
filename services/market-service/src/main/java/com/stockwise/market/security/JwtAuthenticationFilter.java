package com.stockwise.market.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String path = request.getRequestURI();

        if (path.equals("/health") || path.startsWith("/actuator")) {
            filterChain.doFilter(request, response);
            return;
        }

        // For WebSocket handshake requests, token is already validated
        // by JwtAuthHandshakeInterceptor and stored in session attributes.
        // We only need to skip re-validation here to avoid double-work.
        if (request.getRequestURI().startsWith("/ws/")) {
            filterChain.doFilter(request, response);
            return;
        }

        // For REST endpoints: validate Authorization header
        String authHeader = request.getHeader("Authorization");

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            if (jwtTokenProvider.validateToken(token)) {
                String tokenType = jwtTokenProvider.getTokenType(token);
                if (!"access".equals(tokenType)) {
                    response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                    response.setContentType("application/json");
                    response.getWriter().write("{\"error\":\"INVALID_TOKEN_TYPE\",\"message\":\"Only access tokens are allowed\"}");
                    return;
                }

                String userId = jwtTokenProvider.getUserIdFromToken(token);
                String role = jwtTokenProvider.getRoleFromToken(token);
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                userId, null,
                                List.of(new SimpleGrantedAuthority(role)));
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        }

        filterChain.doFilter(request, response);
    }
}
