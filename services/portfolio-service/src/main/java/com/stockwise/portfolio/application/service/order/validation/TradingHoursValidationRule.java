package com.stockwise.portfolio.application.service.order.validation;

import com.stockwise.portfolio.application.service.order.ports.OrderValidationRule;
import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.UUID;

/**
 * Validation rule enforcing trading session hours (BR-104).
 * Checks that orders are placed on weekdays (Monday to Friday) and during active trading windows:
 * - Morning session: 09:00 to 11:30
 * - Afternoon session: 13:00 to 15:00
 * Can be disabled in configurations (`trading.hours.enabled=false`) to ease testing.
 */
@Component
@Order(2)
public class TradingHoursValidationRule implements OrderValidationRule {

    private final boolean tradingHoursEnabled;
    private final Clock clock;

    public TradingHoursValidationRule(
            @Value("${trading.hours.enabled:true}") boolean tradingHoursEnabled,
            Clock clock) {
        this.tradingHoursEnabled = tradingHoursEnabled;
        this.clock = clock;
    }

    /**
     * Validates that the current time is within trading hours and days.
     */
    @Override
    public void validate(UUID userId, String symbol, String type, Integer quantity, BigDecimal price) {
        if (!tradingHoursEnabled) {
            return;
        }
        LocalDateTime now = LocalDateTime.now(clock);
        DayOfWeek day = now.getDayOfWeek();
        if (day == DayOfWeek.SATURDAY || day == DayOfWeek.SUNDAY) {
            throw new BadRequestException("Orders can only be placed during trading days (Monday to Friday)");
        }
        LocalTime time = now.toLocalTime();
        boolean inMorning = !time.isBefore(LocalTime.of(9, 0)) && !time.isAfter(LocalTime.of(11, 30));
        boolean inAfternoon = !time.isBefore(LocalTime.of(13, 0)) && !time.isAfter(LocalTime.of(15, 0));
        if (!inMorning && !inAfternoon) {
            throw new BadRequestException("Orders can only be placed during trading hours (09:00-11:30, 13:00-15:00)");
        }
    }
}
