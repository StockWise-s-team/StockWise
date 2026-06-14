package com.stockwise.gateway.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockwise.gateway.service.ProxyForwarder;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequiredArgsConstructor
public class PortfolioProxyController {

    private final ObjectMapper objectMapper;
    private final ProxyForwarder proxyForwarder;

    @Value("${portfolio-service.url}")
    private String portfolioServiceUrl;

    @GetMapping("/portfolio")
    public ResponseEntity<String> getPortfolio(
            HttpServletRequest request,
            Authentication authentication,
            @RequestHeader HttpHeaders headers
    ) {
        String url = buildPortfolioUrl(request, authentication);
        return proxyForwarder.forwardUrl("Portfolio service", url, HttpMethod.GET, null, headers);
    }

    @GetMapping("/portfolio/pnl")
    public ResponseEntity<String> getPnl(
            HttpServletRequest request,
            Authentication authentication,
            @RequestHeader HttpHeaders headers
    ) {
        String url = buildPortfolioUrl(request, authentication);
        return proxyForwarder.forwardUrl("Portfolio service", url, HttpMethod.GET, null, headers);
    }

    @PostMapping("/portfolio/order")
    public ResponseEntity<String> placeOrder(
            Authentication authentication,
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers
    ) throws JsonProcessingException {
        Map<String, Object> order = body == null || body.isBlank()
                ? new LinkedHashMap<>()
                : objectMapper.readValue(body, new TypeReference<Map<String, Object>>() {});
        order.put("userId", authenticatedUserId(authentication));

        String url = normalizeBaseUrl(portfolioServiceUrl) + "/portfolio/order";
        return proxyForwarder.forwardUrl("Portfolio service", url, HttpMethod.POST, objectMapper.writeValueAsString(order), headers);
    }

    @RequestMapping("/portfolio/**")
    public ResponseEntity<String> forwardPortfolioFallback(
            HttpServletRequest request,
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers
    ) {
        HttpMethod method = HttpMethod.valueOf(request.getMethod());
        return proxyForwarder.forward("Portfolio service", portfolioServiceUrl, request, method, body, headers);
    }

    private String buildPortfolioUrl(HttpServletRequest request, Authentication authentication) {
        UriComponentsBuilder builder = UriComponentsBuilder
                .fromHttpUrl(normalizeBaseUrl(portfolioServiceUrl))
                .path(request.getRequestURI());

        request.getParameterMap().forEach((key, values) -> {
            if (!key.equals("userId")) {
                builder.queryParam(key, (Object[]) values);
            }
        });
        builder.queryParam("userId", authenticatedUserId(authentication));
        return builder.build().toUriString();
    }

    private String authenticatedUserId(Authentication authentication) {
        return authentication.getName();
    }

    private String normalizeBaseUrl(String baseUrl) {
        return baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
    }
}
