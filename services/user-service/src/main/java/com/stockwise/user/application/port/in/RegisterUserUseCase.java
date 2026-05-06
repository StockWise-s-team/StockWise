package com.stockwise.user.application.port.in;

import com.stockwise.user.dto.AuthResponse;
import com.stockwise.user.dto.RegisterRequest;

public interface RegisterUserUseCase {
    AuthResponse register(RegisterRequest request);
}
