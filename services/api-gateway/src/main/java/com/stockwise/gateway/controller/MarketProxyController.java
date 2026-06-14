package com.stockwise.gateway.controller;

import com.stockwise.gateway.service.ProxyForwarder;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class MarketProxyController {

    private final ProxyForwarder proxyForwarder;

    @Value("${market-service.url}")
    private String marketServiceUrl;

    @RequestMapping("/market/**")
    public ResponseEntity<String> forwardMarket(
            HttpServletRequest request,
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers
    ) {
        HttpMethod method = HttpMethod.valueOf(request.getMethod());
        return proxyForwarder.forward("Market service", marketServiceUrl, request, method, body, headers);
    }
}
