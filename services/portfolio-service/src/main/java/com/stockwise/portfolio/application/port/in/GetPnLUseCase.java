package com.stockwise.portfolio.application.port.in;

import java.math.BigDecimal;
import java.util.UUID;

public interface GetPnLUseCase {
    BigDecimal getTotalPnl(UUID userId);
}
