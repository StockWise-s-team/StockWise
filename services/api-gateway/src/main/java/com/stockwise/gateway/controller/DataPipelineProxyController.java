package com.stockwise.gateway.controller;

import com.stockwise.gateway.service.ProxyForwarder;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

@RestController
@RequiredArgsConstructor
public class DataPipelineProxyController {

    private final ProxyForwarder proxyForwarder;

    @Value("${data-pipeline-service.url}")
    private String dataPipelineServiceUrl;

    @GetMapping("/pipeline/progress")
    public ResponseEntity<StreamingResponseBody> streamPipelineProgress(
            HttpServletRequest request,
            @RequestHeader HttpHeaders headers
    ) {
        return proxyForwarder.stream("Data pipeline service", dataPipelineServiceUrl, request, HttpMethod.GET, null, headers);
    }

    @RequestMapping(
            value = {
                    "/tracked-symbols",
                    "/tracked-symbols/**",
                    "/company-wiki",
                    "/company-wiki/**",
                    "/scripts/seed",
                    "/synthesis/trigger",
                    "/pipeline/status",
                    "/pipeline/progress/poll",
                    "/pipeline/runs",
                    "/pipeline/runs/**",
                    "/user/tracked-symbols",
                    "/user/news-sources"
            },
            method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.DELETE, RequestMethod.PUT}
    )
    public ResponseEntity<String> forwardDataPipeline(
            HttpServletRequest request,
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers
    ) {
        HttpMethod method = HttpMethod.valueOf(request.getMethod());
        return proxyForwarder.forward("Data pipeline service", dataPipelineServiceUrl, request, method, body, headers);
    }

    @PatchMapping("/news-sources/{sourceId}")
    public ResponseEntity<String> toggleNewsSource(
            HttpServletRequest request,
            @RequestBody(required = false) String body,
            @RequestHeader HttpHeaders headers
    ) {
        return proxyForwarder.forward("Data pipeline service", dataPipelineServiceUrl, request, HttpMethod.PATCH, body, headers);
    }

    @RequestMapping(value = "/news-sources", method = RequestMethod.GET)
    public ResponseEntity<String> listNewsSources(
            HttpServletRequest request,
            @RequestHeader HttpHeaders headers
    ) {
        return proxyForwarder.forward("Data pipeline service", dataPipelineServiceUrl, request, HttpMethod.GET, null, headers);
    }
}
