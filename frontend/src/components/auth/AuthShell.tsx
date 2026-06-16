"use client";

import { useState, type InputHTMLAttributes, type ReactNode } from "react";
import Link from "next/link";
import {
  Activity,
  BarChart3,
  CheckCircle2,
  Eye,
  EyeOff,
  LockKeyhole,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { clsx } from "clsx";

interface AuthShellProps {
  children: ReactNode;
  eyebrow: string;
  title: string;
  description: string;
  footerText: string;
  footerLinkLabel: string;
  footerLinkHref: string;
}

const systemChecks = [
  { label: "Market data stream", value: "connected" },
  { label: "Analysis engine", value: "ready" },
  { label: "Secure session", value: "encrypted" },
];

export function AuthShell({
  children,
  eyebrow,
  title,
  description,
  footerText,
  footerLinkLabel,
  footerLinkHref,
}: AuthShellProps) {
  return (
    <main className="relative min-h-screen overflow-hidden bg-terminal-bg font-mono text-terminal-text">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(240,180,41,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(240,180,41,0.035)_1px,transparent_1px)] [background-size:44px_44px]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-32 top-1/3 h-80 w-80 rounded-full bg-terminal-accent/[0.06] blur-3xl"
      />

      <div className="relative mx-auto grid min-h-screen w-full max-w-[1440px] lg:grid-cols-[minmax(0,1.05fr)_minmax(440px,0.95fr)]">
        <section className="hidden border-r border-terminal-border px-10 py-8 lg:flex lg:flex-col xl:px-16 xl:py-12">
          <Brand />

          <div className="my-auto max-w-xl py-16">
            <div className="mb-8 inline-flex items-center gap-2 rounded border border-terminal-accent/30 bg-terminal-accent/[0.06] px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-[0.2em] text-terminal-accent">
              <Activity className="h-3 w-3" />
              Intelligence terminal
            </div>

            <h2 className="font-display text-4xl font-bold uppercase leading-[1.08] tracking-[-0.03em] text-terminal-text xl:text-5xl">
              Read the market.
              <span className="mt-2 block text-terminal-accent">
                Act with context.
              </span>
            </h2>
            <p className="mt-6 max-w-lg text-xs leading-6 text-terminal-muted">
              One operational workspace for market signals, portfolio context,
              and AI-assisted equity research.
            </p>

            <div className="mt-12 border-y border-terminal-border">
              {systemChecks.map((item, index) => (
                <div
                  key={item.label}
                  className={clsx(
                    "grid grid-cols-[24px_1fr_auto] items-center gap-3 py-3",
                    index > 0 && "border-t border-terminal-border"
                  )}
                >
                  <span className="text-[10px] text-terminal-muted">
                    0{index + 1}
                  </span>
                  <span className="text-[10px] uppercase tracking-widest text-terminal-text">
                    {item.label}
                  </span>
                  <span className="flex items-center gap-1.5 text-[9px] uppercase tracking-wider text-terminal-green">
                    <CheckCircle2 className="h-3 w-3" />
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between text-[9px] uppercase tracking-[0.18em] text-terminal-muted">
            <span>StockWise / Access node</span>
            <span>VN market intelligence</span>
          </div>
        </section>

        <section className="flex min-h-screen flex-col px-5 py-6 sm:px-8 lg:px-12 xl:px-20">
          <div className="flex items-center justify-between lg:justify-end">
            <div className="lg:hidden">
              <Brand />
            </div>
            <div className="flex items-center gap-2 text-[9px] uppercase tracking-[0.16em] text-terminal-muted">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-green" />
              System online
            </div>
          </div>

          <div className="my-auto w-full max-w-[460px] self-center py-10">
            <div className="mb-8 flex items-center gap-3 border-b border-terminal-border pb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
                <Terminal className="h-4 w-4 text-terminal-accent" />
              </div>
              <div>
                <p className="text-[9px] uppercase tracking-[0.22em] text-terminal-muted">
                  {eyebrow}
                </p>
                <p className="mt-0.5 text-[10px] uppercase tracking-wider text-terminal-text">
                  Identity verification
                </p>
              </div>
            </div>

            <header className="mb-8">
              <h1 className="font-display text-3xl font-bold uppercase tracking-[-0.02em] text-terminal-text sm:text-4xl">
                {title}
              </h1>
              <p className="mt-3 text-xs leading-5 text-terminal-muted">
                {description}
              </p>
            </header>

            {children}

            <div className="mt-8 flex items-center justify-between border-t border-terminal-border pt-5 text-[10px]">
              <span className="text-terminal-muted">{footerText}</span>
              <Link
                href={footerLinkHref}
                className="font-semibold uppercase tracking-wider text-terminal-accent transition-colors hover:text-terminal-amber focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-terminal-accent/50"
              >
                {footerLinkLabel} <span aria-hidden="true">-&gt;</span>
              </Link>
            </div>
          </div>

          <div className="flex items-center justify-center gap-2 text-[9px] uppercase tracking-[0.14em] text-terminal-muted">
            <ShieldCheck className="h-3 w-3 text-terminal-green" />
            TLS encrypted session
          </div>
        </section>
      </div>
    </main>
  );
}

function Brand() {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-terminal-accent/50"
      aria-label="StockWise home"
    >
      <span className="relative flex h-9 w-9 items-center justify-center rounded border border-terminal-accent/40 bg-terminal-accent/[0.08]">
        <BarChart3 className="h-4 w-4 text-terminal-accent" />
        <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full border-2 border-terminal-bg bg-terminal-green" />
      </span>
      <span>
        <span className="block font-display text-sm font-bold uppercase tracking-[0.2em] text-terminal-accent">
          StockWise
        </span>
        <span className="mt-0.5 block text-[8px] uppercase tracking-[0.22em] text-terminal-muted">
          Market intelligence
        </span>
      </span>
    </Link>
  );
}

interface AuthFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: ReactNode;
}

export function AuthField({
  label,
  hint,
  id,
  type = "text",
  className,
  ...props
}: AuthFieldProps) {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-4">
        <label
          htmlFor={id}
          className="text-[10px] font-semibold uppercase tracking-[0.16em] text-terminal-text"
        >
          {label}
        </label>
        {hint && <span className="text-[9px] text-terminal-muted">{hint}</span>}
      </div>
      <div className="group relative">
        <input
          id={id}
          type={isPassword && showPassword ? "text" : type}
          className={clsx(
            "h-11 w-full rounded border border-terminal-border bg-terminal-surface px-3 text-xs text-terminal-text outline-none transition-all placeholder:text-terminal-muted/50 hover:border-terminal-muted focus:border-terminal-accent/60 focus:bg-terminal-accent/[0.025] focus:ring-2 focus:ring-terminal-accent/10 disabled:cursor-not-allowed disabled:opacity-50",
            isPassword && "pr-11",
            className
          )}
          {...props}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword((current) => !current)}
            className="absolute right-0 top-0 flex h-11 w-11 items-center justify-center text-terminal-muted transition-colors hover:text-terminal-accent focus-visible:outline-none focus-visible:text-terminal-accent"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        )}
      </div>
    </div>
  );
}

export function AuthError({ message }: { message: string }) {
  return (
    <div
      role="alert"
      aria-live="polite"
      className="flex items-start gap-2.5 rounded border border-terminal-red/30 bg-terminal-red/[0.06] px-3 py-2.5 text-[10px] leading-5 text-terminal-red"
    >
      <LockKeyhole className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <span>{message}</span>
    </div>
  );
}

export function AuthSubmitButton({
  loading,
  idleLabel,
  loadingLabel,
}: {
  loading: boolean;
  idleLabel: string;
  loadingLabel: string;
}) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="group flex h-11 w-full items-center justify-center gap-2 rounded border border-terminal-accent/50 bg-terminal-accent px-4 text-[10px] font-bold uppercase tracking-[0.18em] text-terminal-bg transition-all hover:bg-terminal-amber hover:shadow-[0_0_24px_rgba(240,180,41,0.12)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-terminal-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-terminal-bg disabled:cursor-not-allowed disabled:border-terminal-border disabled:bg-terminal-border disabled:text-terminal-muted disabled:shadow-none"
    >
      {loading && (
        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-terminal-bg/30 border-t-terminal-bg" />
      )}
      {loading ? loadingLabel : idleLabel}
      {!loading && (
        <span
          aria-hidden="true"
          className="transition-transform group-hover:translate-x-1"
        >
          -&gt;
        </span>
      )}
    </button>
  );
}
