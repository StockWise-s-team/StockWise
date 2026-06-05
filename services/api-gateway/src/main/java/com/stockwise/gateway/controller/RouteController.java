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
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
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

    @Value("${market-service.url}")
    private String marketServiceUrl;

    @PostMapping("/auth/register")
    public ResponseEntity<?> register(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/register", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/login")
    public ResponseEntity<?> login(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/login", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/refresh")
    public ResponseEntity<?> refresh(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/refresh", HttpMethod.POST, body, headers);
    }

    @PostMapping("/auth/refresh-token-cookie")
    public ResponseEntity<?> refreshTokenCookie(@RequestBody String body, @RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/refresh-token-cookie", HttpMethod.POST, body, headers);
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

    @GetMapping("/market/price/{symbol}")
    public ResponseEntity<?> marketPrice(@PathVariable String symbol, @RequestHeader HttpHeaders headers) {
        return forwardGet(marketServiceUrl + "/market/price/" + symbol, headers);
    }

    @GetMapping("/market/ratio/{symbol}")
    public ResponseEntity<?> marketRatio(@PathVariable String symbol, @RequestHeader HttpHeaders headers) {
        return forwardGet(marketServiceUrl + "/market/ratio/" + symbol, headers);
    }

    @GetMapping("/market/ohlc/{symbol}")
    public ResponseEntity<?> marketOhlc(
            @PathVariable String symbol,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate,
            @RequestHeader HttpHeaders headers
    ) {
        StringBuilder url = new StringBuilder(marketServiceUrl + "/market/ohlc/" + symbol);
        boolean hasQuery = false;

        if (startDate != null && !startDate.isBlank()) {
            url.append(hasQuery ? '&' : '?').append("startDate=").append(startDate);
            hasQuery = true;
        }
        if (endDate != null && !endDate.isBlank()) {
            url.append(hasQuery ? '&' : '?').append("endDate=").append(endDate);
        }

        return forwardGet(url.toString(), headers);
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
