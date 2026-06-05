package com.stockwise.portfolio.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.time.Clock;

/**
 * General application configurations.
 */
@Configuration
public class AppConfig {

    /**
     * Declares a Clock bean using the system default time zone.
     * This clock bean is used by validation rules (like TradingHoursValidationRule)
     * to check trading hours, allowing it to be easily mocked or replaced in tests.
     *
     * @return the default Clock instance
     */
    @Bean
    public Clock clock() {
        return Clock.systemDefaultZone();
    }
}
