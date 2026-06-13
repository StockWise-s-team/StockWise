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

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setValidationError(null);

    if (password !== confirmPassword) {
      setValidationError("Passwords do not match. Please try again.");
      return;
    }

    if (password.length < 6) {
      setValidationError("Password must be at least 6 characters.");
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

        <AuthField
          id="password"
          label="Password"
          hint="Minimum 6 characters"
          type="password"
          value={password}
          onChange={(event) => {
            setPassword(event.target.value);
            setError(null);
            setValidationError(null);
          }}
          placeholder="Create a secure password"
          autoComplete="new-password"
          minLength={6}
          required
        />

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
          minLength={6}
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
