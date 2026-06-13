package com.stockwise.user.application.service;

import com.stockwise.user.application.port.in.AuthenticateUserUseCase;
import com.stockwise.user.application.port.in.RegisterUserUseCase;
import com.stockwise.user.application.port.out.UserPersistencePort;
import com.stockwise.user.adapter.out.persistence.TokenManagementService;
import com.stockwise.user.domain.entity.User;
import com.stockwise.user.dto.AuthResponse;
import com.stockwise.user.dto.ChangePasswordRequest;
import com.stockwise.user.dto.LoginRequest;
import com.stockwise.user.dto.RegisterRequest;
import com.stockwise.user.dto.UpdateProfileRequest;
import com.stockwise.user.dto.UserDto;
import com.stockwise.user.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService implements RegisterUserUseCase, AuthenticateUserUseCase {

    private final UserPersistencePort userPersistencePort;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final TokenManagementService tokenManagementService;

    @Override
    public AuthResponse register(RegisterRequest request) {
        if (userPersistencePort.findByEmail(request.email()).isPresent()) {
            throw new EmailAlreadyExistsException("Email already registered");
        }

        User user = new User();
        user.setEmail(request.email());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setRole("ROLE_USER");
        user.setFullName(request.fullName());
        user.setCreatedAt(LocalDateTime.now());

        userPersistencePort.save(user);

        String accessToken = jwtTokenProvider.generateAccessToken(
                user.getId().toString(), user.getEmail(), user.getRole());
        String refreshToken = jwtTokenProvider.generateRefreshToken(user.getId().toString());

        String refreshJti = jwtTokenProvider.getRefreshTokenJti(refreshToken);
        long refreshTtlMs = jwtTokenProvider.getExpiration(refreshToken) - System.currentTimeMillis();
        tokenManagementService.registerRefreshToken(
                refreshJti, user.getId().toString(), Duration.ofMillis(refreshTtlMs));

        log.info("User registered: {}", user.getEmail());
        return new AuthResponse(accessToken, refreshToken, toUserDto(user));
    }

    @Override
    public AuthResponse authenticate(LoginRequest request) {
        Optional<User> userOpt = userPersistencePort.findByEmail(request.email());

        if (userOpt.isEmpty()) {
            throw new InvalidCredentialsException("Invalid email or password");
        }

        User user = userOpt.get();

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new InvalidCredentialsException("Invalid email or password");
        }

        String accessToken = jwtTokenProvider.generateAccessToken(
                user.getId().toString(), user.getEmail(), user.getRole());
        String refreshToken = jwtTokenProvider.generateRefreshToken(user.getId().toString());

        String refreshJti = jwtTokenProvider.getRefreshTokenJti(refreshToken);
        long refreshTtlMs = jwtTokenProvider.getExpiration(refreshToken) - System.currentTimeMillis();
        tokenManagementService.registerRefreshToken(
                refreshJti, user.getId().toString(), Duration.ofMillis(refreshTtlMs));

        log.info("User authenticated: {}", user.getEmail());
        return new AuthResponse(accessToken, refreshToken, toUserDto(user));
    }

    public UserDto getCurrentUser(String userId) {
        UUID id = UUID.fromString(userId);
        User user = userPersistencePort.findById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found"));
        return toUserDto(user);
    }

    public UserDto updateProfile(String userId, UpdateProfileRequest request) {
        UUID id = UUID.fromString(userId);
        User user = userPersistencePort.findById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found"));
        user.setFullName(request.fullName());
        User saved = userPersistencePort.save(user);
        log.info("Profile updated for user: {}", user.getEmail());
        return toUserDto(saved);
    }

    public void changePassword(String userId, ChangePasswordRequest request) {
        UUID id = UUID.fromString(userId);
        User user = userPersistencePort.findById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found"));

        if (!passwordEncoder.matches(request.currentPassword(), user.getPasswordHash())) {
            throw new IncorrectPasswordException("Current password is incorrect");
        }

        user.setPasswordHash(passwordEncoder.encode(request.newPassword()));
        userPersistencePort.save(user);
        log.info("Password changed for user: {}", user.getEmail());
    }

    private UserDto toUserDto(User user) {
        return new UserDto(user.getId(), user.getEmail(), user.getRole(), user.getFullName(), user.getCreatedAt());
    }

    public static class EmailAlreadyExistsException extends RuntimeException {
        public EmailAlreadyExistsException(String message) {
            super(message);
        }
    }

    public static class InvalidCredentialsException extends RuntimeException {
        public InvalidCredentialsException(String message) {
            super(message);
        }
    }

    public static class UserNotFoundException extends RuntimeException {
        public UserNotFoundException(String message) {
            super(message);
        }
    }

    public static class IncorrectPasswordException extends RuntimeException {
        public IncorrectPasswordException(String message) {
            super(message);
        }
    }
}
