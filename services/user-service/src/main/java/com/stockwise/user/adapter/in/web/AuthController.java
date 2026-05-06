package com.stockwise.user.adapter.in.web;

import com.stockwise.user.application.port.in.AuthenticateUserUseCase;
import com.stockwise.user.application.port.in.RegisterUserUseCase;
import com.stockwise.user.dto.AuthResponse;
import com.stockwise.user.dto.LoginRequest;
import com.stockwise.user.dto.RegisterRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final RegisterUserUseCase registerUserUseCase;
    private final AuthenticateUserUseCase authenticateUserUseCase;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(registerUserUseCase.register(request));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authenticateUserUseCase.authenticate(request));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refresh() {
        String mockAccessToken = "mock-access-token-" + UUID.randomUUID();
        String mockRefreshToken = "mock-refresh-token-" + UUID.randomUUID();
        return ResponseEntity.ok(new AuthResponse(mockAccessToken, mockRefreshToken));
    }
}
