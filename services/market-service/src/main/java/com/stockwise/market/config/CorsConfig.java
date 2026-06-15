package com.stockwise.market.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Value("${cors.allowed-origins:http://localhost:3000,http://localhost:13000}")
    private String corsAllowedOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        List<String> origins = Arrays.stream(corsAllowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isBlank())
                .collect(Collectors.toList());

        registry.addMapping("/market/**")
                .allowedOriginPatterns(origins.isEmpty() ? new String[]{"*"} : origins.toArray(new String[0]))
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
