package com.stockwise.gateway.service;

import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.util.StreamUtils;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

import java.io.IOException;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

@Slf4j
@Component
public class ProxyForwarder {

    private final RestTemplate restTemplate = new RestTemplate();
    private final WebClient webClient = WebClient.builder().build();
    private static final byte[] SSE_CONNECTED = ": connected\n\n".getBytes(StandardCharsets.UTF_8);

    @Value("${gateway.dev-user-id:00000000-0000-0000-0000-000000000001}")
    private String gatewayDevUserId;

    public ResponseEntity<String> forward(
            String serviceName,
            String baseUrl,
            HttpServletRequest request,
            HttpMethod method,
            String body,
            HttpHeaders requestHeaders
    ) {
        return forwardUrl(serviceName, buildUrl(baseUrl, request.getRequestURI(), request.getQueryString()), method, body, requestHeaders);
    }

    public ResponseEntity<String> forwardUrl(
            String serviceName,
            String url,
            HttpMethod method,
            String body,
            HttpHeaders requestHeaders
    ) {
        try {
            HttpHeaders upstreamHeaders = copyRequestHeaders(requestHeaders, body);
            WebClient.RequestBodySpec spec = webClient.method(method)
                    .uri(url)
                    .headers(headers -> headers.addAll(upstreamHeaders));

            ResponseEntity<String> upstreamResponse = (body != null && !body.isBlank()
                    ? spec.bodyValue(body)
                    : spec)
                    .exchangeToMono(response -> response.toEntity(String.class))
                    .timeout(Duration.ofSeconds(10))
                    .block();

            if (upstreamResponse == null) {
                return serviceUnavailable(serviceName);
            }

            return ResponseEntity.status(upstreamResponse.getStatusCode())
                    .headers(copyResponseHeaders(upstreamResponse.getHeaders()))
                    .body(upstreamResponse.getBody());
        } catch (HttpStatusCodeException e) {
            log.warn("Gateway upstream error [{} {}]: status={}, body={}", method, url, e.getStatusCode(), e.getResponseBodyAsString());
            return ResponseEntity.status(e.getStatusCode())
                    .headers(copyResponseHeaders(e.getResponseHeaders()))
                    .body(e.getResponseBodyAsString());
        } catch (Exception e) {
            log.error("Gateway forward error [{} {}]: {}", method, url, e.getMessage(), e);
            return serviceUnavailable(serviceName);
        }
    }

    public ResponseEntity<StreamingResponseBody> stream(
            String serviceName,
            String baseUrl,
            HttpServletRequest request,
            HttpMethod method,
            String body,
            HttpHeaders requestHeaders
    ) {
        String url = buildUrl(baseUrl, request.getRequestURI(), request.getQueryString());
        HttpHeaders upstreamHeaders = copyRequestHeaders(requestHeaders, body);
        StreamingResponseBody stream = outputStream -> {
            try {
                outputStream.write(SSE_CONNECTED);
                flushQuietly(outputStream, method, url);

                restTemplate.execute(URI.create(url), method, clientRequest -> {
                    upstreamHeaders.forEach((key, values) -> values.forEach(value -> clientRequest.getHeaders().add(key, value)));
                    if (body != null && !body.isBlank()) {
                        StreamUtils.copy(body, StandardCharsets.UTF_8, clientRequest.getBody());
                    }
                }, clientResponse -> {
                    StreamUtils.copy(clientResponse.getBody(), outputStream);
                    flushQuietly(outputStream, method, url);
                    return null;
                });
            } catch (HttpStatusCodeException e) {
                log.warn("Gateway stream upstream error [{} {}]: status={}, body={}", method, url, e.getStatusCode(), e.getResponseBodyAsString());
                try {
                    writeSseUpstreamError(outputStream, e);
                } catch (IOException writeError) {
                    log.debug("Unable to write SSE upstream error event for [{} {}]: {}", method, url, writeError.getMessage());
                }
            } catch (Exception e) {
                if (isExpectedStreamClose(e)) {
                    log.warn("Gateway stream closed [{} {}]: {}", method, url, e.getMessage());
                } else {
                    log.error("Gateway stream error [{} {}]: {}", method, url, e.getMessage(), e);
                }
                try {
                    writeSseError(outputStream, serviceName);
                } catch (IOException writeError) {
                    log.debug("Unable to write SSE error event for [{} {}]: {}", method, url, writeError.getMessage());
                }
            }
        };

        return ResponseEntity.ok()
                .contentType(MediaType.TEXT_EVENT_STREAM)
                .header(HttpHeaders.CACHE_CONTROL, "no-cache")
                .header("X-Accel-Buffering", "no")
                .body(stream);
    }

    private String buildUrl(String baseUrl, String path, String queryString) {
        String normalizedBase = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        String url = normalizedBase + path;
        if (queryString != null && !queryString.isBlank()) {
            url += "?" + queryString;
        }
        return url;
    }

    private HttpHeaders copyRequestHeaders(HttpHeaders requestHeaders, String body) {
        HttpHeaders upstreamHeaders = new HttpHeaders();
        requestHeaders.forEach((key, values) -> {
            if (!isHopByHopRequestHeader(key)) {
                upstreamHeaders.addAll(key, values);
            }
        });
        applyGatewayIdentityHeaders(upstreamHeaders);
        if (body != null && !body.isBlank() && upstreamHeaders.getContentType() == null) {
            upstreamHeaders.setContentType(MediaType.APPLICATION_JSON);
        }
        return upstreamHeaders;
    }

    private HttpHeaders copyResponseHeaders(HttpHeaders upstreamHeaders) {
        HttpHeaders responseHeaders = new HttpHeaders();
        if (upstreamHeaders == null) {
            return responseHeaders;
        }
        upstreamHeaders.forEach((key, values) -> {
            if (!isHopByHopResponseHeader(key)) {
                responseHeaders.addAll(key, values);
            }
        });
        return responseHeaders;
    }

    private boolean isHopByHopRequestHeader(String header) {
        return header.equalsIgnoreCase(HttpHeaders.CONTENT_LENGTH)
                || header.equalsIgnoreCase(HttpHeaders.HOST)
                || header.equalsIgnoreCase(HttpHeaders.CONNECTION)
                || header.equalsIgnoreCase("X-User-Id")
                || header.equalsIgnoreCase("X-Role")
                || header.equalsIgnoreCase("X-Dev-User-Id");
    }

    private boolean isHopByHopResponseHeader(String header) {
        return header.equalsIgnoreCase(HttpHeaders.CONTENT_LENGTH)
                || header.equalsIgnoreCase(HttpHeaders.TRANSFER_ENCODING)
                || header.equalsIgnoreCase(HttpHeaders.CONNECTION)
                || header.toLowerCase().startsWith("access-control-")
                || header.equalsIgnoreCase("Vary");
    }

    private void applyGatewayIdentityHeaders(HttpHeaders headers) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null
                || !authentication.isAuthenticated()
                || authentication.getName() == null
                || "anonymousUser".equals(authentication.getName())) {
            if (StringUtils.hasText(gatewayDevUserId)) {
                headers.set("X-User-Id", gatewayDevUserId);
                headers.set("X-Role", "user");
            }
            return;
        }

        headers.set("X-User-Id", authentication.getName());
        authentication.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .findFirst()
                .map(this::normalizeRole)
                .ifPresent(role -> headers.set("X-Role", role));
    }

    private String normalizeRole(String role) {
        if (role == null || role.isBlank()) {
            return "user";
        }
        return role.replaceFirst("^ROLE_", "").toLowerCase();
    }

    private void writeSseError(java.io.OutputStream outputStream, String serviceName) throws IOException {
        String payload = "{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"" + serviceName + " unavailable\"}";
        outputStream.write(("event: error\ndata: " + payload + "\n\n").getBytes(StandardCharsets.UTF_8));
        outputStream.flush();
    }

    private void writeSseUpstreamError(java.io.OutputStream outputStream, HttpStatusCodeException error) throws IOException {
        String payload = "{\"error\":\"UPSTREAM_ERROR\",\"status\":" + error.getStatusCode().value()
                + ",\"body\":\"" + escapeJson(error.getResponseBodyAsString()) + "\"}";
        outputStream.write(("event: error\ndata: " + payload + "\n\n").getBytes(StandardCharsets.UTF_8));
        outputStream.flush();
    }

    private ResponseEntity<String> serviceUnavailable(String serviceName) {
        return ResponseEntity.status(503)
                .contentType(MediaType.APPLICATION_JSON)
                .body("{\"error\":\"SERVICE_UNAVAILABLE\",\"message\":\"" + serviceName + " unavailable\"}");
    }

    private void flushQuietly(java.io.OutputStream outputStream, HttpMethod method, String url) {
        try {
            outputStream.flush();
        } catch (Exception e) {
            log.debug("Ignoring SSE flush failure [{} {}]: {}", method, url, e.getMessage());
        }
    }

    private boolean isExpectedStreamClose(Exception e) {
        String message = e.getMessage();
        if (message == null) {
            return false;
        }
        String normalized = message.toLowerCase();
        return normalized.contains("premature eof")
                || normalized.contains("response not usable")
                || normalized.contains("broken pipe")
                || normalized.contains("connection reset")
                || normalized.contains("stream closed");
    }

    private String escapeJson(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
