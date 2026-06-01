"use client";

import { useState, FormEvent } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import { TrendingUp } from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { register } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match. Please try again.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
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
    <main className="flex min-h-screen flex-col items-center justify-center bg-[#06110a] px-4">
      {/* Brand mark */}
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary shadow-lg shadow-primary/30">
          <TrendingUp className="h-6 w-6 text-ink" strokeWidth={2.5} />
        </div>
        <span className="text-xl font-semibold tracking-tight text-on-dark">
          StockWise
        </span>
      </div>

      {/* Auth card */}
      <div className="w-full max-w-sm rounded-xl bg-[#0d2b1a] p-8 shadow-2xl shadow-black/60 border border-emerald-900/50">
        <h1 className="mb-1 text-2xl font-semibold text-[#e8f5ef]">Create Account</h1>
        <p className="mb-6 text-sm text-emerald-600">Start your investment journey</p>

        {error && (
          <div className="mb-4 rounded-md border border-trading-down/30 bg-trading-down/10 px-4 py-3 text-sm text-trading-down">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="fullName"
              className="mb-1.5 block text-xs font-medium text-emerald-500"
            >
              Full Name
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="h-10 w-full rounded-md border border-emerald-800/50 bg-[#162e22] px-4 text-sm text-[#e8f5ef] placeholder:text-emerald-700 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
              placeholder="Optional"
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="mb-1.5 block text-xs font-medium text-emerald-500"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setError(null); }}
              className="h-10 w-full rounded-md border border-emerald-800/50 bg-[#162e22] px-4 text-sm text-[#e8f5ef] placeholder:text-emerald-700 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-1.5 block text-xs font-medium text-emerald-500"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(null); }}
              className="h-10 w-full rounded-md border border-emerald-800/50 bg-[#162e22] px-4 text-sm text-[#e8f5ef] placeholder:text-emerald-700 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
              placeholder="At least 6 characters"
              required
            />
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="mb-1.5 block text-xs font-medium text-emerald-500"
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => { setConfirmPassword(e.target.value); setError(null); }}
              className="h-10 w-full rounded-md border border-emerald-800/50 bg-[#162e22] px-4 text-sm text-[#e8f5ef] placeholder:text-emerald-700 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
              placeholder="Re-enter your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 flex h-10 w-full items-center justify-center rounded-md bg-[#10b981] px-6 text-sm font-semibold text-[#02281f] shadow-lg shadow-emerald-500/20 transition-colors hover:bg-[#059669] hover:shadow-xl hover:shadow-emerald-500/40 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 animate-spin text-ink"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Creating account...
              </span>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        <div className="mt-6 flex items-center justify-center">
          <span className="text-sm text-emerald-600">
            Already have an account?&nbsp;
          </span>
          <a
            href="/login"
            className="text-sm font-semibold text-primary transition-colors hover:text-primary-active"
          >
            Sign In
          </a>
        </div>
      </div>

      {/* Footer note */}
      <p className="mt-6 text-xs text-emerald-700">
        Secure, AI-powered stock analysis platform
      </p>
    </main>
  );
}
