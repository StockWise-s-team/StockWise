package com.stockwise.user.application.service;

import com.stockwise.user.application.port.in.AuthenticateUserUseCase;
import com.stockwise.user.application.port.in.RegisterUserUseCase;
import com.stockwise.user.application.port.out.UserPersistencePort;
import com.stockwise.user.domain.entity.User;
import com.stockwise.user.dto.AuthResponse;
import com.stockwise.user.dto.LoginRequest;
import com.stockwise.user.dto.RegisterRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService implements RegisterUserUseCase, AuthenticateUserUseCase {

    private final UserPersistencePort userPersistencePort;
    private final PasswordEncoder passwordEncoder;

    @Override
    public AuthResponse register(RegisterRequest request) {
        if (userPersistencePort.findByEmail(request.email()).isPresent()) {
            throw new IllegalArgumentException("Email already registered");
        }

        User user = new User();
        user.setId(UUID.randomUUID());
        user.setEmail(request.email());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setRole("ROLE_USER");
        user.setCreatedAt(LocalDateTime.now());

        userPersistencePort.save(user);

        String mockAccessToken = "mock-access-token-" + UUID.randomUUID();
        String mockRefreshToken = "mock-refresh-token-" + UUID.randomUUID();

        log.info("User registered: {}", user.getEmail());
        return new AuthResponse(mockAccessToken, mockRefreshToken);
    }

    @Override
    public AuthResponse authenticate(LoginRequest request) {
        Optional<User> userOpt = userPersistencePort.findByEmail(request.email());

        if (userOpt.isEmpty()) {
            throw new IllegalArgumentException("Invalid email or password");
        }

        User user = userOpt.get();

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Invalid email or password");
        }

        String mockAccessToken = "mock-access-token-" + UUID.randomUUID();
        String mockRefreshToken = "mock-refresh-token-" + UUID.randomUUID();

        log.info("User authenticated: {}", user.getEmail());
        return new AuthResponse(mockAccessToken, mockRefreshToken);
    }
}
