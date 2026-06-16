"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import api from "@/lib/api";
import {
  AuthError,
  AuthField,
  AuthShell,
  AuthSubmitButton,
} from "@/components/auth/AuthShell";

type Step = "REQUEST_OTP" | "VERIFY_OTP" | "RESET_PASSWORD" | "SUCCESS";

const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;

function getPasswordStrength(pw: string): { label: string; color: string; pct: number } {
  if (!pw) return { label: "", color: "", pct: 0 };
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[a-z]/.test(pw)) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pw)) score++;
  if (score <= 2) return { label: "Weak", color: "bg-terminal-red", pct: 33 };
  if (score <= 3) return { label: "Fair", color: "bg-terminal-amber", pct: 60 };
  if (score === 4) return { label: "Good", color: "bg-terminal-accent", pct: 80 };
  return { label: "Strong", color: "bg-terminal-green", pct: 100 };
}

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<Step>("REQUEST_OTP");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const router = useRouter();

  // Localized error helper
  const handleApiError = (err: any) => {
    const errorCode = err.response?.data?.error || err.response?.data?.err;
    const fallbackMessage = err.response?.data?.message || "Đã xảy ra lỗi. Vui lòng thử lại.";

    const errorTranslations: Record<string, string> = {
      USER_NOT_FOUND: "Email không tồn tại trên hệ thống. Vui lòng kiểm tra lại.",
      INVALID_OTP: "Mã OTP không đúng hoặc đã hết hạn.",
      SAME_PASSWORD: "Mật khẩu mới phải khác mật khẩu hiện tại.",
      VALIDATION_ERROR: "Thông tin nhập không hợp lệ. Vui lòng kiểm tra lại.",
    };

    setError(errorTranslations[errorCode] || fallbackMessage);
  };

  const handleRequestOtp = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post("/auth/forgot-password", { email });
      setSuccessMessage("Mã OTP đã được gửi đến email của bạn.");
      setStep("VERIFY_OTP");
    } catch (err: any) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post("/auth/verify-otp", { email, otp });
      setSuccessMessage("Xác thực OTP thành công. Vui lòng đặt mật khẩu mới.");
      setStep("RESET_PASSWORD");
    } catch (err: any) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!PASSWORD_REGEX.test(password)) {
      setError(
        "Mật khẩu phải chứa ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."
      );
      return;
    }

    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/reset-password", { email, otp, newPassword: password });
      setStep("SUCCESS");
    } catch (err: any) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  };

  const strength = getPasswordStrength(password);

  if (step === "SUCCESS") {
    return (
      <AuthShell
        eyebrow="Access protocol / 03"
        title="Password updated"
        description="Mật khẩu của bạn đã được cập nhật thành công. Vui lòng đăng nhập bằng mật khẩu mới."
        footerText="Ready to trade?"
        footerLinkLabel="Sign in to your account"
        footerLinkHref="/login"
      >
        <div className="flex flex-col items-center justify-center space-y-6 py-8 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-terminal-green/30 bg-terminal-green/[0.06] text-terminal-green">
            <CheckCircle2 className="h-8 w-8" />
          </div>
          <div className="space-y-2">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-terminal-text">
              Reset Complete
            </h3>
            <p className="text-xs text-terminal-muted leading-relaxed max-w-[280px]">
              Tài khoản của bạn đã được cập nhật mật khẩu mới và các phiên đăng nhập cũ đã bị vô hiệu hóa.
            </p>
          </div>
          <button
            onClick={() => router.push("/login")}
            className="flex h-11 w-full items-center justify-center rounded border border-terminal-accent/50 bg-terminal-accent px-4 text-[10px] font-bold uppercase tracking-[0.18em] text-terminal-bg transition-all hover:bg-terminal-amber focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-terminal-accent/50"
          >
            Đăng nhập ngay -&gt;
          </button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      eyebrow={`Access protocol / 0${step === "REQUEST_OTP" ? 3 : step === "VERIFY_OTP" ? 4 : 5}`}
      title={
        step === "REQUEST_OTP"
          ? "Forgot Password"
          : step === "VERIFY_OTP"
          ? "Verify OTP"
          : "Reset Password"
      }
      description={
        step === "REQUEST_OTP"
          ? "Nhập email của bạn để nhận mã xác thực OTP khôi phục mật khẩu."
          : step === "VERIFY_OTP"
          ? `Mã OTP đã được gửi đến email: ${email}. Vui lòng nhập mã để tiếp tục.`
          : "Đặt mật khẩu mới để bảo mật tài khoản StockWise của bạn."
      }
      footerText="Remembered password?"
      footerLinkLabel="Sign in"
      footerLinkHref="/login"
    >
      {step === "REQUEST_OTP" && (
        <form onSubmit={handleRequestOtp} className="space-y-5">
          {error && <AuthError message={error} />}

          <AuthField
            id="email"
            label="Email address"
            type="email"
            value={email}
            onChange={(event) => {
              setEmail(event.target.value);
              setError(null);
            }}
            placeholder="analyst@company.com"
            autoComplete="email"
            autoFocus
            required
          />

          <div className="pt-1">
            <AuthSubmitButton
              loading={loading}
              idleLabel="Send OTP Code"
              loadingLabel="Sending OTP"
            />
          </div>
        </form>
      )}

      {step === "VERIFY_OTP" && (
        <form onSubmit={handleVerifyOtp} className="space-y-5">
          {error && <AuthError message={error} />}
          {successMessage && (
            <div className="flex items-start gap-2.5 rounded border border-terminal-green/30 bg-terminal-green/[0.06] px-3 py-2.5 text-[10px] leading-5 text-terminal-green">
              <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          <AuthField
            id="otp"
            label="OTP Code (6 digits)"
            type="text"
            inputMode="numeric"
            pattern="\d{6}"
            maxLength={6}
            value={otp}
            onChange={(event) => {
              setOtp(event.target.value.replace(/\D/g, ""));
              setError(null);
            }}
            placeholder="123456"
            autoFocus
            required
          />

          <div className="flex items-center justify-between text-[10px]">
            <button
              type="button"
              onClick={() => {
                setStep("REQUEST_OTP");
                setError(null);
                setSuccessMessage(null);
              }}
              className="flex items-center gap-1.5 text-terminal-muted hover:text-terminal-text transition-colors"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Quay lại
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={async () => {
                setError(null);
                setLoading(true);
                try {
                  await api.post("/auth/forgot-password", { email });
                  setSuccessMessage("Mã OTP mới đã được gửi thành công.");
                } catch (err: any) {
                  handleApiError(err);
                } finally {
                  setLoading(false);
                }
              }}
              className="text-terminal-accent hover:text-terminal-amber hover:underline transition-colors disabled:opacity-50"
            >
              Gửi lại mã OTP
            </button>
          </div>

          <div className="pt-1">
            <AuthSubmitButton
              loading={loading}
              idleLabel="Verify Code"
              loadingLabel="Verifying"
            />
          </div>
        </form>
      )}

      {step === "RESET_PASSWORD" && (
        <form onSubmit={handleResetPassword} className="space-y-5">
          {error && <AuthError message={error} />}
          {successMessage && (
            <div className="flex items-start gap-2.5 rounded border border-terminal-green/30 bg-terminal-green/[0.06] px-3 py-2.5 text-[10px] leading-5 text-terminal-green">
              <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          <div>
            <AuthField
              id="password"
              label="New Password"
              hint="≥8 chars · A-Z · a-z · 0-9 · !@#…"
              type="password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setError(null);
              }}
              placeholder="Create a strong password"
              autoComplete="new-password"
              minLength={8}
              autoFocus
              required
            />
            {password && (
              <div className="mt-2 space-y-1">
                <div className="h-1 w-full overflow-hidden rounded-full bg-terminal-border">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${strength.color}`}
                    style={{ width: `${strength.pct}%` }}
                  />
                </div>
                <p className="text-[9px] uppercase tracking-wider text-terminal-muted">
                  Strength:{" "}
                  <span
                    className={`font-semibold ${
                      strength.label === "Strong" ? "text-terminal-green"
                      : strength.label === "Good" ? "text-terminal-accent"
                      : strength.label === "Fair" ? "text-terminal-amber"
                      : "text-terminal-red"
                    }`}
                  >
                    {strength.label}
                  </span>
                </p>
                <ul className="space-y-0.5 text-[9px] text-terminal-muted">
                  <li className={/[A-Z]/.test(password) ? "text-terminal-green" : ""}>· Uppercase letter</li>
                  <li className={/[a-z]/.test(password) ? "text-terminal-green" : ""}>· Lowercase letter</li>
                  <li className={/\d/.test(password) ? "text-terminal-green" : ""}>· Number</li>
                  <li className={/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password) ? "text-terminal-green" : ""}>· Special character</li>
                  <li className={password.length >= 8 ? "text-terminal-green" : ""}>· At least 8 characters</li>
                </ul>
              </div>
            )}
          </div>

          <AuthField
            id="confirmPassword"
            label="Confirm New Password"
            type="password"
            value={confirmPassword}
            onChange={(event) => {
              setConfirmPassword(event.target.value);
              setError(null);
            }}
            placeholder="Repeat your password"
            autoComplete="new-password"
            minLength={8}
            required
          />

          <div className="pt-1">
            <AuthSubmitButton
              loading={loading}
              idleLabel="Reset Password"
              loadingLabel="Resetting"
            />
          </div>
        </form>
      )}
    </AuthShell>
  );
}
