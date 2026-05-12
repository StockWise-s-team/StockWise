package com.stockwise.gateway.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestTemplate;

@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class RouteController {

    private final RestTemplate restTemplate = new RestTemplate();

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

    @GetMapping("/me")
    public ResponseEntity<?> me(@RequestHeader HttpHeaders headers) {
        return forward(userServiceUrl + "/auth/me", HttpMethod.GET, null, headers);
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

            HttpEntity<String> entity = new HttpEntity<>(body, upstreamHeaders);
            ResponseEntity<String> upstreamResponse = restTemplate.exchange(url, method, entity, String.class);

            HttpHeaders responseHeaders = new HttpHeaders();
            upstreamResponse.getHeaders().forEach((key, values) -> {
                if (!key.equalsIgnoreCase("Content-Length") && !key.equalsIgnoreCase("Transfer-Encoding")) {
                    responseHeaders.addAll(key, values);
                }
            });

            return ResponseEntity.status(upstreamResponse.getStatusCode())
                    .headers(responseHeaders)
                    .body(upstreamResponse.getBody());

        } catch (HttpStatusCodeException e) {
            log.warn("Gateway upstream error [{} {}]: status={}, body={}", method, url, e.getStatusCode(), e.getResponseBodyAsString());
            return ResponseEntity.status(e.getStatusCode())
                    .header("Content-Type", "application/json")
                    .body(e.getResponseBodyAsString());
        } catch (Exception e) {
            log.error("Gateway forward error [{} {}]: {}", method, url, e.getMessage(), e);
            return ResponseEntity.status(503)
                    .header("Content-Type", "application/json")
                    .body("{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"User service unavailable: " + e.getMessage() + "\"}");
        }
    }
}
