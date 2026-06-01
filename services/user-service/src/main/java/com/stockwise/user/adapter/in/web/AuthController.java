package com.stockwise.user.adapter.in.web;

import com.stockwise.user.adapter.out.persistence.TokenManagementService;
import com.stockwise.user.application.service.UserService;
import com.stockwise.user.application.port.in.AuthenticateUserUseCase;
import com.stockwise.user.application.port.in.RegisterUserUseCase;
import com.stockwise.user.dto.AuthResponse;
import com.stockwise.user.dto.ChangePasswordRequest;
import com.stockwise.user.dto.LoginRequest;
import com.stockwise.user.dto.RefreshRequest;
import com.stockwise.user.dto.RegisterRequest;
import com.stockwise.user.dto.UpdateProfileRequest;
import com.stockwise.user.dto.UserDto;
import com.stockwise.user.security.JwtTokenProvider;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Duration;
import java.util.Arrays;

@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private static final String REFRESH_TOKEN_COOKIE_NAME = "refresh_token";
    private static final String SAME_SITE_COOKIE_ATTRIBUTE = "SameSite=Strict";

    private final RegisterUserUseCase registerUserUseCase;
    private final AuthenticateUserUseCase authenticateUserUseCase;
    private final UserService userService;
    private final JwtTokenProvider jwtTokenProvider;
    private final TokenManagementService tokenManagementService;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(
            @Valid @RequestBody RegisterRequest request,
            HttpServletResponse response) {
        AuthResponse authResponse = registerUserUseCase.register(request);
        setRefreshTokenCookie(response, authResponse.refreshToken());
        return ResponseEntity.ok(new AuthResponse(authResponse.accessToken(), null, authResponse.user()));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(
            @Valid @RequestBody LoginRequest request,
            HttpServletResponse response) {
        AuthResponse authResponse = authenticateUserUseCase.authenticate(request);
        setRefreshTokenCookie(response, authResponse.refreshToken());
        return ResponseEntity.ok(new AuthResponse(authResponse.accessToken(), null, authResponse.user()));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refresh(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            @Valid @RequestBody RefreshRequest request,
            HttpServletResponse response) {
        String oldAccessToken = null;
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            oldAccessToken = authHeader.substring(7);
        }

        String refreshToken = request.refreshToken();
        if (refreshToken == null) {
            throw new SecurityException("Refresh token is required");
        }

        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new SecurityException("Invalid refresh token");
        }
        String tokenType = jwtTokenProvider.getTokenType(refreshToken);
        if (!"refresh".equals(tokenType)) {
            throw new SecurityException("Invalid token type: expected refresh token");
        }

        String refreshJti = jwtTokenProvider.getRefreshTokenJti(refreshToken);
        if (refreshJti == null || !tokenManagementService.isRefreshTokenValid(refreshJti)) {
            throw new SecurityException("Refresh token has been revoked or expired");
        }

        String userId = jwtTokenProvider.getUserIdFromToken(refreshToken);
        UserDto user = userService.getCurrentUser(userId);

        if (oldAccessToken != null) {
            String oldAccessJti = jwtTokenProvider.getTokenId(oldAccessToken);
            long ttlMs = jwtTokenProvider.getExpiration(oldAccessToken) - System.currentTimeMillis();
            if (ttlMs > 0) {
                tokenManagementService.blacklistAccessToken(oldAccessJti, Duration.ofMillis(ttlMs));
            }
        }

        String newAccessToken = jwtTokenProvider.generateAccessToken(userId, user.email(), user.role());
        String newRefreshToken = jwtTokenProvider.generateRefreshToken(userId);

        tokenManagementService.revokeRefreshToken(refreshJti);

        String newRefreshJti = jwtTokenProvider.getRefreshTokenJti(newRefreshToken);
        long refreshTtlMs = jwtTokenProvider.getExpiration(newRefreshToken) - System.currentTimeMillis();
        tokenManagementService.registerRefreshToken(newRefreshJti, userId, Duration.ofMillis(refreshTtlMs));

        setRefreshTokenCookie(response, newRefreshToken);
        return ResponseEntity.ok(new AuthResponse(newAccessToken, null, user));
    }

    @GetMapping("/me")
    public ResponseEntity<UserDto> me(@RequestHeader("Authorization") String authHeader) {
        String token = authHeader.substring(7);
        String userId = jwtTokenProvider.getUserIdFromToken(token);
        return ResponseEntity.ok(userService.getCurrentUser(userId));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(
            @RequestHeader("Authorization") String authHeader,
            HttpServletRequest request,
            HttpServletResponse response) {
        String token = authHeader.substring(7);
        String userId = jwtTokenProvider.getUserIdFromToken(token);

        clearRefreshTokenCookie(response);
        log.info("User logged out: {}", userId);
        return ResponseEntity.ok().build();
    }

    @PutMapping("/profile")
    public ResponseEntity<UserDto> updateProfile(
            @RequestHeader("Authorization") String authHeader,
            @Valid @RequestBody UpdateProfileRequest request) {
        String token = authHeader.substring(7);
        String userId = jwtTokenProvider.getUserIdFromToken(token);
        return ResponseEntity.ok(userService.updateProfile(userId, request));
    }

    @PutMapping("/password")
    public ResponseEntity<Void> changePassword(
            @RequestHeader("Authorization") String authHeader,
            @Valid @RequestBody ChangePasswordRequest request) {
        String token = authHeader.substring(7);
        String userId = jwtTokenProvider.getUserIdFromToken(token);
        userService.changePassword(userId, request);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/refresh-token-cookie")
    public ResponseEntity<AuthResponse> refreshTokenCookie(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            HttpServletRequest request,
            HttpServletResponse response) {

        String refreshToken = extractRefreshTokenFromCookie(request);
        if (refreshToken == null) {
            throw new SecurityException("Refresh token not found in cookie");
        }

        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new SecurityException("Invalid refresh token");
        }
        String tokenType = jwtTokenProvider.getTokenType(refreshToken);
        if (!"refresh".equals(tokenType)) {
            throw new SecurityException("Invalid token type: expected refresh token");
        }

        String refreshJti = jwtTokenProvider.getRefreshTokenJti(refreshToken);
        if (refreshJti == null || !tokenManagementService.isRefreshTokenValid(refreshJti)) {
            throw new SecurityException("Refresh token has been revoked or expired");
        }

        String oldAccessToken = null;
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            oldAccessToken = authHeader.substring(7);
        }

        String userId = jwtTokenProvider.getUserIdFromToken(refreshToken);
        UserDto user = userService.getCurrentUser(userId);

        if (oldAccessToken != null) {
            String oldAccessJti = jwtTokenProvider.getTokenId(oldAccessToken);
            long ttlMs = jwtTokenProvider.getExpiration(oldAccessToken) - System.currentTimeMillis();
            if (ttlMs > 0) {
                tokenManagementService.blacklistAccessToken(oldAccessJti, Duration.ofMillis(ttlMs));
            }
        }

        String newAccessToken = jwtTokenProvider.generateAccessToken(userId, user.email(), user.role());
        String newRefreshToken = jwtTokenProvider.generateRefreshToken(userId);

        tokenManagementService.revokeRefreshToken(refreshJti);

        String newRefreshJti = jwtTokenProvider.getRefreshTokenJti(newRefreshToken);
        long refreshTtlMs = jwtTokenProvider.getExpiration(newRefreshToken) - System.currentTimeMillis();
        tokenManagementService.registerRefreshToken(newRefreshJti, userId, Duration.ofMillis(refreshTtlMs));

        setRefreshTokenCookie(response, newRefreshToken);
        return ResponseEntity.ok(new AuthResponse(newAccessToken, null, user));
    }

    private void setRefreshTokenCookie(HttpServletResponse response, String refreshToken) {
        long maxAgeSeconds = (jwtTokenProvider.getExpiration(refreshToken) - System.currentTimeMillis()) / 1000;
        String cookieValue = String.format(
                "%s=%s; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=%d",
                REFRESH_TOKEN_COOKIE_NAME, refreshToken, maxAgeSeconds);
        response.addHeader("Set-Cookie", cookieValue);
    }

    private void clearRefreshTokenCookie(HttpServletResponse response) {
        String cookieValue = String.format(
                "%s=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0",
                REFRESH_TOKEN_COOKIE_NAME);
        response.addHeader("Set-Cookie", cookieValue);
    }

    private String extractRefreshTokenFromCookie(HttpServletRequest request) {
        if (request.getCookies() == null) {
            return null;
        }
        return Arrays.stream(request.getCookies())
                .filter(c -> REFRESH_TOKEN_COOKIE_NAME.equals(c.getName()))
                .map(Cookie::getValue)
                .findFirst()
                .orElse(null);
    }
}
