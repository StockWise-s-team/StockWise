package com.stockwise.gateway.filter;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

@Slf4j
@Component
@Order(3)
public class CookieToAuthorizationFilter extends OncePerRequestFilter {

    private static final String REFRESH_TOKEN_COOKIE = "refresh_token";
    private static final String REFRESH_ENDPOINT = "/auth/refresh";

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String path = request.getRequestURI();
        String method = request.getMethod();

        if ("POST".equals(method) && REFRESH_ENDPOINT.equals(path)) {
            String refreshToken = extractCookie(request, REFRESH_TOKEN_COOKIE);
            if (refreshToken != null) {
                String body = readRequestBody(request);
                String newBody = injectRefreshToken(body, refreshToken);
                filterChain.doFilter(
                        new CachedBodyHttpServletRequest(request, newBody),
                        response);
                return;
            }
        }

        filterChain.doFilter(request, response);
    }

    private String readRequestBody(HttpServletRequest request) throws IOException {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(request.getInputStream(), StandardCharsets.UTF_8))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            return sb.toString();
        }
    }

    private String injectRefreshToken(String body, String refreshToken) {
        if (body == null || body.isEmpty()) {
            return String.format("{\"refreshToken\":\"%s\"}", refreshToken);
        }
        if (body.contains("\"refreshToken\"")) {
            return body.replaceAll("\"refreshToken\"\\s*:\\s*\"[^\"]*\"", "\"refreshToken\":\"" + refreshToken + "\"");
        }
        if (body.endsWith("}")) {
            return body.substring(0, body.length() - 1) + ",\"refreshToken\":\"" + refreshToken + "\"}";
        }
        return body;
    }

    private String extractCookie(HttpServletRequest request, String name) {
        Cookie[] cookies = request.getCookies();
        if (cookies == null) return null;
        for (Cookie cookie : cookies) {
            if (name.equals(cookie.getName())) {
                return cookie.getValue();
            }
        }
        return null;
    }
}
