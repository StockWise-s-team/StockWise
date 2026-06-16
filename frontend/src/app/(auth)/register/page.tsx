"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/providers/AuthProvider";
import {
  AuthError,
  AuthField,
  AuthShell,
  AuthSubmitButton,
} from "@/components/auth/AuthShell";

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

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const { register, error, setError, user, isLoading } = useAuth();
  const router = useRouter();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/dashboard");
    }
  }, [isLoading, user, router]);

  if (isLoading || user) return null;

  const strength = getPasswordStrength(password);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setValidationError(null);

    if (!PASSWORD_REGEX.test(password)) {
      setValidationError(
        "Password must be at least 8 characters and contain uppercase, lowercase, number, and special character."
      );
      return;
    }

    if (password !== confirmPassword) {
      setValidationError("Passwords do not match. Please try again.");
      return;
    }

    setLoading(true);
    try {
      await register(email, password, fullName || undefined);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell
      eyebrow="Access protocol / 02"
      title="Create account"
      description="Provision a secure identity for your StockWise intelligence workspace."
      footerText="Already registered?"
      footerLinkLabel="Sign in"
      footerLinkHref="/login"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {(validationError || error) && (
          <AuthError message={validationError || error || ""} />
        )}

        <AuthField
          id="fullName"
          label="Full name"
          hint="Optional"
          type="text"
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
          placeholder="Nguyen Van A"
          autoComplete="name"
          autoFocus
        />

        <AuthField
          id="email"
          label="Email address"
          type="email"
          value={email}
          onChange={(event) => {
            setEmail(event.target.value);
            setError(null);
            setValidationError(null);
          }}
          placeholder="analyst@company.com"
          autoComplete="email"
          required
        />

        <div>
          <AuthField
            id="password"
            label="Password"
            hint="≥8 chars · A-Z · a-z · 0-9 · !@#…"
            type="password"
            value={password}
            onChange={(event) => {
              setPassword(event.target.value);
              setError(null);
              setValidationError(null);
            }}
            placeholder="Create a strong password"
            autoComplete="new-password"
            minLength={8}
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
          label="Confirm password"
          type="password"
          value={confirmPassword}
          onChange={(event) => {
            setConfirmPassword(event.target.value);
            setError(null);
            setValidationError(null);
          }}
          placeholder="Repeat your password"
          autoComplete="new-password"
          minLength={8}
          required
        />

        <div className="pt-2">
          <AuthSubmitButton
            loading={loading}
            idleLabel="Provision account"
            loadingLabel="Creating identity"
          />
        </div>
      </form>
    </AuthShell>
  );
}
