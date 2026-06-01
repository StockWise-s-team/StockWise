package com.stockwise.gateway.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;

@Slf4j
@Controller
@RequestMapping("/auth")
@RequiredArgsConstructor
public class RouteController {

    private final WebClient webClient;

    @Value("${user-service.url}")
    private String userServiceUrl;

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/register", HttpMethod.POST, body, headers);
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/login", HttpMethod.POST, body, headers);
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refresh(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/refresh", HttpMethod.POST, body, headers);
    }

    @PostMapping("/refresh-token-cookie")
    public ResponseEntity<?> refreshTokenCookie(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/refresh-token-cookie", HttpMethod.POST, body, headers);
    }

    @GetMapping("/me")
    public ResponseEntity<?> me(@RequestHeader HttpHeaders headers) {
        return forwardGet(userServiceUrl + "/auth/me", headers);
    }

    @PutMapping("/profile")
    public ResponseEntity<?> profile(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/profile", HttpMethod.PUT, body, headers);
    }

    @PutMapping("/password")
    public ResponseEntity<?> password(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/password", HttpMethod.PUT, body, headers);
    }

    private ResponseEntity<?> forward(String url, HttpMethod method, String body, HttpHeaders requestHeaders) {
        try {
            HttpHeaders upstreamHeaders = new HttpHeaders();
            upstreamHeaders.setContentType(MediaType.APPLICATION_JSON);
            requestHeaders.forEach((key, values) -> {
                if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Host")) {
                    upstreamHeaders.addAll(key, values);
                }
            });

            WebClient.RequestBodySpec spec = webClient.method(method)
                    .uri(url)
                    .headers(h -> h.addAll(upstreamHeaders));

            Mono<ResponseEntity<String>> responseMono;
            if (body != null && !body.isEmpty()) {
                responseMono = spec.bodyValue(body)
                        .retrieve()
                        .toEntity(String.class);
            } else {
                responseMono = spec.retrieve()
                        .toEntity(String.class);
            }

            ResponseEntity<String> upstreamResponse = responseMono
                    .timeout(Duration.ofSeconds(10))
                    .block();

            if (upstreamResponse == null) {
                return ResponseEntity.status(503)
                        .header("Content-Type", "application/json")
                        .body("{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"Service temporarily unavailable. Please try again later.\"}");
            }

            // Set-Cookie headers from user-service (HttpOnly refresh token) are automatically forwarded
            HttpHeaders responseHeaders = new HttpHeaders();
            upstreamResponse.getHeaders().forEach((key, values) -> {
                if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Transfer-Encoding")) {
                    responseHeaders.addAll(key, values);
                }
            });

            return ResponseEntity.status(upstreamResponse.getStatusCode())
                    .headers(responseHeaders)
                    .body(upstreamResponse.getBody());

        } catch (Exception e) {
            log.error("Gateway forward error [{} {}]: {}", method, url, e.getMessage(), e);
            return ResponseEntity.status(503)
                    .header("Content-Type", "application/json")
                    .body("{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"Service temporarily unavailable. Please try again later.\"}");
        }
    }

    private ResponseEntity<?> forwardGet(String url, HttpHeaders requestHeaders) {
        try {
            HttpHeaders upstreamHeaders = new HttpHeaders();
            requestHeaders.forEach((key, values) -> {
                if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Host")) {
                    upstreamHeaders.addAll(key, values);
                }
            });

            ResponseEntity<String> upstreamResponse = webClient.get()
                    .uri(url)
                    .headers(h -> h.addAll(upstreamHeaders))
                    .retrieve()
                    .toEntity(String.class)
                    .timeout(Duration.ofSeconds(10))
                    .block();

            if (upstreamResponse == null) {
                return ResponseEntity.status(503)
                        .header("Content-Type", "application/json")
                        .body("{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"Service temporarily unavailable. Please try again later.\"}");
            }

            // Set-Cookie headers from user-service (HttpOnly refresh token) are automatically forwarded
            HttpHeaders responseHeaders = new HttpHeaders();
            upstreamResponse.getHeaders().forEach((key, values) -> {
                if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Transfer-Encoding")) {
                    responseHeaders.addAll(key, values);
                }
            });

            return ResponseEntity.status(upstreamResponse.getStatusCode())
                    .headers(responseHeaders)
                    .body(upstreamResponse.getBody());

        } catch (Exception e) {
            log.error("Gateway forward error [GET {}]: {}", url, e.getMessage(), e);
            return ResponseEntity.status(503)
                    .header("Content-Type", "application/json")
                    .body("{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"Service temporarily unavailable. Please try again later.\"}");
        }
    }
}
