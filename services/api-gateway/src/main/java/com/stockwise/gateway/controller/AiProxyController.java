package com.stockwise.gateway.controller;

import com.stockwise.gateway.service.ProxyForwarder;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

@RestController
@RequiredArgsConstructor
public class AiProxyController {

    private final ProxyForwarder proxyForwarder;

    @Value("${ai-service.url}")
    private String aiServiceUrl;

    @GetMapping("/api/v1/health")
    public ResponseEntity<String> health(
            HttpServletRequest request,
            @RequestHeader HttpHeaders headers
    ) {
        return proxyForwarder.forward("AI service", aiServiceUrl, request, HttpMethod.GET, null, headers);
    }

    @PostMapping("/api/v1/advisor/chat")
    public ResponseEntity<StreamingResponseBody> chat(
            HttpServletRequest request,
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers
    ) {
        return proxyForwarder.stream("AI service", aiServiceUrl, request, HttpMethod.POST, body, headers);
    }

    @GetMapping("/api/v1/advisor/chat/stream")
    public ResponseEntity<StreamingResponseBody> chatStream(
            HttpServletRequest request,
            @RequestHeader HttpHeaders headers
    ) {
        return proxyForwarder.stream("AI service", aiServiceUrl, request, HttpMethod.GET, null, headers);
    }

    @RequestMapping({"/api/v1/advisor/**", "/api/v1/admin/**"})
    public ResponseEntity<String> forwardAi(
            HttpServletRequest request,
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers
    ) {
        HttpMethod method = HttpMethod.valueOf(request.getMethod());
        return proxyForwarder.forward("AI service", aiServiceUrl, request, method, body, headers);
    }
}
