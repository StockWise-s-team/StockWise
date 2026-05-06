package com.stockwise.user.application.port.in;

import com.stockwise.user.dto.AuthResponse;
import com.stockwise.user.dto.LoginRequest;

public interface AuthenticateUserUseCase {
    AuthResponse authenticate(LoginRequest request);
}
