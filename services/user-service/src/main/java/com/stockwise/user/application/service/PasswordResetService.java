package com.stockwise.user.application.service;

import com.stockwise.user.application.port.out.UserPersistencePort;
import com.stockwise.user.domain.entity.User;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * Orchestrates the full "Forgot Password via OTP" flow.
 *
 * Flow:
 *  1. forgotPassword(email)  → validate email exists, generate OTP, store in Redis, send email
 *  2. verifyOtp(email, otp)  → check OTP in Redis; throw if invalid/expired
 *  3. resetPassword(email, otp, newPassword) → verify OTP, hash+save new password, delete OTP
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PasswordResetService {

    private final UserPersistencePort userPersistencePort;
    private final OtpService otpService;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;

    // ─── Use Case 1: Request OTP ─────────────────────────────────────────────

    public void forgotPassword(String email) {
        // Verify user exists — but return a generic message to avoid email enumeration attacks
        userPersistencePort.findByEmail(email)
                .orElseThrow(() -> new UserService.UserNotFoundException(
                        "No account found with that email address"));

        String otp = otpService.generateAndStoreOtp(email);
        emailService.sendOtpEmail(email, otp);
        log.info("Forgot-password OTP generated and email dispatched for: {}", email);
    }

    // ─── Use Case 2: Verify OTP ───────────────────────────────────────────────

    public void verifyOtp(String email, String otp) {
        if (!otpService.verifyOtp(email, otp)) {
            throw new InvalidOtpException("OTP is invalid or has expired");
        }
    }

    // ─── Use Case 3: Reset Password ───────────────────────────────────────────

    public void resetPassword(String email, String otp, String newPassword) {
        // Fetch user
        User user = userPersistencePort.findByEmail(email)
                .orElseThrow(() -> new UserService.UserNotFoundException(
                        "No account found with that email address"));

        // Re-verify OTP
        if (!otpService.verifyOtp(email, otp)) {
            throw new InvalidOtpException("OTP is invalid or has expired");
        }

        // Guard against reuse of the same password
        if (passwordEncoder.matches(newPassword, user.getPasswordHash())) {
            throw new UserService.SamePasswordException(
                    "New password must be different from the current password");
        }

        // Persist new password
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        userPersistencePort.save(user);

        // Invalidate OTP — one-time use guarantee
        otpService.deleteOtp(email);

        log.info("Password successfully reset for user: {}", email);
    }

    // ─── Exception Types ─────────────────────────────────────────────────────

    public static class InvalidOtpException extends RuntimeException {
        public InvalidOtpException(String message) {
            super(message);
        }
    }
}
