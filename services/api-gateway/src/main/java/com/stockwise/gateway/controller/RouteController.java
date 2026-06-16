package com.stockwise.gateway.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.DeleteMapping;
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
@RequestMapping
@RequiredArgsConstructor
public class RouteController {

    private final WebClient webClient;

    @Value("${user-service.url}")
    private String userServiceUrl;

    @PostMapping("/auth/register")
    public ResponseEntity<?> register(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/register", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/login")
    public ResponseEntity<?> login(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/login", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/refresh")
    public ResponseEntity<?> refresh(@RequestBody(required = false) String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/refresh", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/refresh-token-cookie")
    public ResponseEntity<?> refreshTokenCookie(@RequestBody(required = false) String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/refresh-token-cookie", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/forgot-password")
    public ResponseEntity<?> forgotPassword(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/forgot-password", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/verify-otp")
    public ResponseEntity<?> verifyOtp(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/verify-otp", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/reset-password")
    public ResponseEntity<?> resetPassword(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/reset-password", HttpMethod.POST, body, headers);
    }

    @GetMapping("/auth/me")
    public ResponseEntity<?> me(@RequestHeader HttpHeaders headers) {
        return forwardGet(userServiceUrl + "/auth/me", headers);
    }

    @PutMapping("/auth/profile")
    public ResponseEntity<?> profile(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/profile", HttpMethod.PUT, body, headers);
    }

    @PutMapping("/auth/password")
    public ResponseEntity<?> password(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/password", HttpMethod.PUT, body, headers);
    }

    private ResponseEntity<?> forwardGet(String url, HttpHeaders requestHeaders) {
        return forward(url, HttpMethod.GET, null, requestHeaders);
    }

    private ResponseEntity<?> forward(String url, HttpMethod method, String body, HttpHeaders requestHeaders) {
        try {
            HttpHeaders upstreamHeaders = copyRequestHeaders(requestHeaders);
            if (body != null && !body.isEmpty()) {
                upstreamHeaders.setContentType(MediaType.APPLICATION_JSON);
            }

            WebClient.RequestBodySpec spec = webClient.method(method)
                    .uri(url)
                    .headers(h -> h.addAll(upstreamHeaders));

            Mono<ResponseEntity<String>> responseMono = body != null && !body.isEmpty()
                    ? spec.bodyValue(body).exchangeToMono(response -> response.toEntity(String.class))
                    : spec.exchangeToMono(response -> response.toEntity(String.class));

            ResponseEntity<String> upstreamResponse = responseMono
                    .timeout(Duration.ofSeconds(10))
                    .block();

            if (upstreamResponse == null) {
                return serviceUnavailable();
            }

            return ResponseEntity.status(upstreamResponse.getStatusCode())
                    .headers(copyResponseHeaders(upstreamResponse.getHeaders()))
                    .body(upstreamResponse.getBody());

        } catch (Exception e) {
            log.error("Gateway forward error [{} {}]: {}", method, url, e.getMessage(), e);
            return serviceUnavailable();
        }
    }

    private HttpHeaders copyRequestHeaders(HttpHeaders requestHeaders) {
        HttpHeaders upstreamHeaders = new HttpHeaders();
        requestHeaders.forEach((key, values) -> {
            if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Host")) {
                upstreamHeaders.addAll(key, values);
            }
        });
        return upstreamHeaders;
    }

    private HttpHeaders copyResponseHeaders(HttpHeaders upstreamHeaders) {
        HttpHeaders responseHeaders = new HttpHeaders();
        upstreamHeaders.forEach((key, values) -> {
            if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Transfer-Encoding")) {
                responseHeaders.addAll(key, values);
            }
        });
        return responseHeaders;
    }

    private ResponseEntity<String> serviceUnavailable() {
        return ResponseEntity.status(503)
                .header("Content-Type", "application/json")
                .body("{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"Service temporarily unavailable. Please try again later.\"}");
    }
}
