package com.stockwise.user.adapter.in.web;

import com.stockwise.user.application.service.UserService;
import com.stockwise.user.application.port.in.AuthenticateUserUseCase;
import com.stockwise.user.application.port.in.RegisterUserUseCase;
import com.stockwise.user.dto.AuthResponse;
import com.stockwise.user.dto.LoginRequest;
import com.stockwise.user.dto.RefreshRequest;
import com.stockwise.user.dto.RegisterRequest;
import com.stockwise.user.dto.UserDto;
import com.stockwise.user.security.JwtTokenProvider;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final RegisterUserUseCase registerUserUseCase;
    private final AuthenticateUserUseCase authenticateUserUseCase;
    private final UserService userService;
    private final JwtTokenProvider jwtTokenProvider;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(registerUserUseCase.register(request));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authenticateUserUseCase.authenticate(request));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refresh(@Valid @RequestBody RefreshRequest request) {
        if (!jwtTokenProvider.validateToken(request.refreshToken())) {
            throw new RuntimeException("Invalid refresh token");
        }
        String userId = jwtTokenProvider.getUserIdFromToken(request.refreshToken());
        UserDto user = userService.getCurrentUser(userId);

        String newAccessToken = jwtTokenProvider.generateAccessToken(userId, user.email(), user.role());
        String newRefreshToken = jwtTokenProvider.generateRefreshToken(userId);

        return ResponseEntity.ok(new AuthResponse(newAccessToken, newRefreshToken, user));
    }

    @GetMapping("/me")
    public ResponseEntity<UserDto> me(@RequestHeader("Authorization") String authHeader) {
        String token = authHeader.substring(7);
        String userId = jwtTokenProvider.getUserIdFromToken(token);
        return ResponseEntity.ok(userService.getCurrentUser(userId));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@RequestHeader("Authorization") String authHeader) {
        String token = authHeader.substring(7);
        String userId = jwtTokenProvider.getUserIdFromToken(token);
        log.info("User logged out: {}", userId);
        return ResponseEntity.ok().build();
    }
}
