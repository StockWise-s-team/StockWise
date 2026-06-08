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

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, error, setError, user, isLoading } = useAuth();
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
    setLoading(true);
    try {
      await login(email, password);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell
      eyebrow="Access protocol / 01"
      title="Welcome back"
      description="Authenticate to continue to your portfolio intelligence workspace."
      footerText="New to StockWise?"
      footerLinkLabel="Create account"
      footerLinkHref="/register"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
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

        <AuthField
          id="password"
          label="Password"
          hint="Secure entry"
          type="password"
          value={password}
          onChange={(event) => {
            setPassword(event.target.value);
            setError(null);
          }}
          placeholder="Enter your password"
          autoComplete="current-password"
          required
        />

        <div className="pt-1">
          <AuthSubmitButton
            loading={loading}
            idleLabel="Enter workspace"
            loadingLabel="Authenticating"
          />
        </div>
      </form>
    </AuthShell>
  );
}
