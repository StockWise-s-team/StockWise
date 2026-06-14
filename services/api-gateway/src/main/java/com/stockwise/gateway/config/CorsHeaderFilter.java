package com.stockwise.gateway.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorsHeaderFilter extends OncePerRequestFilter {

    @Value("${cors.allowed-origins:}")
    private String corsAllowedOrigins;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        applyCorsHeaders(request, response);

        if ("OPTIONS".equalsIgnoreCase(request.getMethod())
                && request.getHeader("Access-Control-Request-Method") != null) {
            response.setStatus(HttpServletResponse.SC_OK);
            return;
        }

        filterChain.doFilter(request, response);
    }

    private void applyCorsHeaders(HttpServletRequest request, HttpServletResponse response) {
        String origin = request.getHeader("Origin");
        if (!StringUtils.hasText(origin) || !isAllowedOrigin(origin)) {
            return;
        }

        response.setHeader("Vary", "Origin,Access-Control-Request-Method,Access-Control-Request-Headers");
        response.setHeader("Access-Control-Allow-Origin", origin);
        response.setHeader("Access-Control-Allow-Credentials", "true");
        response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS,PATCH");

        String requestedHeaders = request.getHeader("Access-Control-Request-Headers");
        response.setHeader(
                "Access-Control-Allow-Headers",
                StringUtils.hasText(requestedHeaders) ? requestedHeaders : "Authorization,Content-Type,Accept,Origin"
        );
        response.setHeader("Access-Control-Max-Age", "3600");
        response.setHeader("Access-Control-Expose-Headers", "Authorization, Set-Cookie, Content-Type");
    }

    private boolean isAllowedOrigin(String origin) {
        return allowedOrigins().contains(origin);
    }

    private List<String> allowedOrigins() {
        if (!StringUtils.hasText(corsAllowedOrigins)) {
            return List.of();
        }
        return Arrays.stream(corsAllowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
    }
}
