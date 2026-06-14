import React from "react";
import { AlertCircle, CheckCircle2, type LucideIcon } from "lucide-react";
import { clsx } from "clsx";

type Tone = "default" | "accent" | "success" | "warning" | "danger" | "muted";

const toneText: Record<Tone, string> = {
  default: "text-terminal-text",
  accent: "text-terminal-accent",
  success: "text-terminal-green",
  warning: "text-terminal-amber",
  danger: "text-terminal-red",
  muted: "text-terminal-muted",
};

const toneBorder: Record<Exclude<Tone, "default" | "muted">, string> = {
  accent: "border-terminal-accent/40 bg-terminal-accent/5 text-terminal-accent",
  success: "border-terminal-green/30 bg-terminal-green/5 text-terminal-green",
  warning: "border-terminal-amber/30 bg-terminal-amber/5 text-terminal-amber",
  danger: "border-terminal-red/30 bg-terminal-red/5 text-terminal-red",
};

export function TerminalSectionHeader({
  icon: Icon,
  title,
  subtitle,
  action,
  className,
}: {
  icon: LucideIcon;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "mb-4 flex items-start justify-between gap-4 border-b border-terminal-border pb-3",
        className
      )}
    >
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
          <Icon className="h-4 w-4 text-terminal-accent" />
        </div>
        <div className="min-w-0">
          <h2 className="font-mono text-sm font-semibold uppercase tracking-widest text-terminal-text">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-0.5 font-mono text-[10px] text-terminal-muted">
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {action}
    </div>
  );
}

export function TerminalMetricCard({
  label,
  value,
  helper,
  tone = "default",
}: {
  label: string;
  value: React.ReactNode;
  helper?: React.ReactNode;
  tone?: Tone;
}) {
  return (
    <div className="rounded border border-terminal-border bg-terminal-surface px-3 py-3 transition-colors hover:border-terminal-accent/30">
      <p className="font-mono text-[10px] uppercase tracking-wider text-terminal-muted">
        {label}
      </p>
      <p className={clsx("mt-2 truncate font-mono text-sm font-semibold", toneText[tone])}>
        {value}
      </p>
      {helper && (
        <p className="mt-1 truncate font-mono text-[10px] text-terminal-muted">
          {helper}
        </p>
      )}
    </div>
  );
}

export function TerminalButton({
  className,
  tone = "accent",
  size = "sm",
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  tone?: "accent" | "success" | "danger" | "muted";
  size?: "xs" | "sm" | "md";
}) {
  const toneClass = {
    accent:
      "border-terminal-accent/40 bg-terminal-accent/5 text-terminal-accent hover:border-terminal-accent/70 hover:bg-terminal-accent/10",
    success:
      "border-terminal-green/40 bg-terminal-green/5 text-terminal-green hover:border-terminal-green/70 hover:bg-terminal-green/10",
    danger:
      "border-terminal-red/40 bg-terminal-red/5 text-terminal-red hover:border-terminal-red/70 hover:bg-terminal-red/10",
    muted:
      "border-terminal-border bg-transparent text-terminal-muted hover:border-terminal-muted hover:text-terminal-text",
  }[tone];
  const sizeClass = {
    xs: "h-7 px-2 text-[9px]",
    sm: "h-8 px-2.5 text-[10px]",
    md: "h-10 px-3 text-xs",
  }[size];

  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center gap-1.5 rounded border font-mono font-semibold uppercase tracking-wider transition-colors disabled:cursor-not-allowed disabled:opacity-40",
        toneClass,
        sizeClass,
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export const TerminalInput = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={clsx(
      "h-10 w-full rounded border border-terminal-border bg-terminal-bg px-3 font-mono text-xs text-terminal-text outline-none transition-colors placeholder:text-terminal-muted/50 hover:border-terminal-muted focus:border-terminal-accent/60 disabled:cursor-not-allowed disabled:opacity-40",
      className
    )}
    {...props}
  />
));

TerminalInput.displayName = "TerminalInput";

export const TerminalSelect = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => (
  <select
    ref={ref}
    className={clsx(
      "h-10 w-full rounded border border-terminal-border bg-terminal-bg px-3 font-mono text-xs text-terminal-text outline-none transition-colors hover:border-terminal-muted focus:border-terminal-accent/60 disabled:cursor-not-allowed disabled:opacity-40",
      className
    )}
    {...props}
  >
    {children}
  </select>
));

TerminalSelect.displayName = "TerminalSelect";

export function TerminalNotice({
  tone,
  children,
  className,
}: {
  tone: "success" | "danger" | "warning";
  children: React.ReactNode;
  className?: string;
}) {
  const Icon = tone === "success" ? CheckCircle2 : AlertCircle;
  const role = tone === "danger" ? "alert" : "status";

  return (
    <div
      role={role}
      className={clsx(
        "flex items-start gap-2 rounded border px-3 py-2.5 font-mono text-[11px] leading-relaxed",
        toneBorder[tone],
        className
      )}
    >
      <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <div className="min-w-0">{children}</div>
    </div>
  );
}

export function TerminalEmptyState({
  icon: Icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description?: string;
}) {
  return (
    <div className="rounded border border-terminal-border bg-terminal-surface px-4 py-8 text-center">
      <Icon className="mx-auto mb-2 h-6 w-6 text-terminal-muted" />
      <p className="font-mono text-xs text-terminal-muted">{title}</p>
      {description && (
        <p className="mt-1 font-mono text-[10px] text-terminal-muted/70">
          {description}
        </p>
      )}
    </div>
  );
}

export function TerminalSkeletonRows({
  rows = 3,
  heightClass = "h-12",
}: {
  rows?: number;
  heightClass?: string;
}) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }, (_, index) => (
        <div
          key={index}
          className={clsx("animate-pulse rounded bg-terminal-surface", heightClass)}
        />
      ))}
    </div>
  );
}

export function TerminalTable({
  headers,
  children,
}: {
  headers: Array<{ label: string; align?: "left" | "right" }>;
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-x-auto rounded border border-terminal-border bg-terminal-surface">
      <table className="w-full min-w-[720px] font-mono text-xs">
        <thead>
          <tr className="border-b border-terminal-border text-[10px] uppercase tracking-wider text-terminal-muted">
            {headers.map((header) => (
              <th
                key={header.label}
                className={clsx(
                  "px-3 py-2.5 font-medium",
                  header.align === "right" ? "text-right" : "text-left"
                )}
              >
                {header.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}
