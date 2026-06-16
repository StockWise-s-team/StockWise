package com.stockwise.user.application.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

/**
 * Service for sending transactional emails via Gmail SMTP.
 * Credentials are read from application.yml environment variables — never hardcoded.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    @Value("${spring.mail.username}")
    private String fromEmail;

    /**
     * Sends an OTP password-reset email asynchronously.
     * Using @Async so the HTTP request is not blocked by SMTP latency.
     */
    @Async
    public void sendOtpEmail(String toEmail, String otp) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject("StockWise — Password Reset OTP");
            helper.setText(buildHtmlBody(otp), true);

            mailSender.send(message);
            log.info("OTP email sent to: {}", toEmail);
        } catch (MessagingException e) {
            log.error("Failed to send OTP email to {}: {}", toEmail, e.getMessage(), e);
            // Not re-throwing: the HTTP response has already been sent (async).
            // The OTP is still in Redis, so the user may retry the forgot-password flow.
        }
    }

    private String buildHtmlBody(String otp) {
        return """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                  <meta charset="UTF-8"/>
                  <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; background:#f4f4f7; margin:0; padding:0; }
                    .container { max-width:480px; margin:40px auto; background:#fff;
                                 border-radius:10px; padding:40px; box-shadow:0 2px 12px rgba(0,0,0,.08); }
                    h2 { color:#1a1a2e; margin-bottom:8px; }
                    .otp-box { font-size:36px; font-weight:700; letter-spacing:8px; color:#4f46e5;
                               text-align:center; padding:20px; background:#f0f0ff;
                               border-radius:8px; margin:24px 0; }
                    .note { color:#6b7280; font-size:14px; }
                    .footer { margin-top:32px; font-size:12px; color:#9ca3af; text-align:center; }
                  </style>
                </head>
                <body>
                  <div class="container">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset the password for your <strong>StockWise</strong> account.</p>
                    <p>Use the OTP below to proceed. It is valid for <strong>5 minutes</strong>.</p>
                    <div class="otp-box">%s</div>
                    <p class="note">If you did not request a password reset, please ignore this email. Your account remains secure.</p>
                    <div class="footer">© 2025 StockWise · This is an automated message, please do not reply.</div>
                  </div>
                </body>
                </html>
                """.formatted(otp);
    }
}
