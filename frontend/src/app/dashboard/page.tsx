"use client";

import Link from "next/link";
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Bot,
  BriefcaseBusiness,
  ChevronRight,
  CircleDollarSign,
  Database,
  FlaskConical,
  LineChart,
  Radio,
  ShieldCheck,
  WalletCards,
} from "lucide-react";
import { clsx } from "clsx";

const portfolio = {
  netWorth: 35_487.84,
  buyingPower: 24_680,
  marketValue: 10_807.84,
  pnl: 1_114.14,
  returnPct: 11.49,
};

const watchlist = [
  { symbol: "NVDA", name: "NVIDIA", price: 118.11, change: 2.17 },
  { symbol: "AAPL", name: "Apple", price: 192.35, change: 1.42 },
  { symbol: "MSFT", name: "Microsoft", price: 424.52, change: 0.86 },
  { symbol: "GOOGL", name: "Alphabet", price: 176.92, change: -0.38 },
];

const allocation = [
  { symbol: "MSFT", value: 3396.16, percent: 31.4 },
  { symbol: "AAPL", value: 1923.5, percent: 17.8 },
  { symbol: "NVDA", value: 1417.32, percent: 13.1 },
  { symbol: "GOOGL", value: 884.6, percent: 8.2 },
];

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

function SectionHeader({
  icon: Icon,
  title,
  subtitle,
  action,
}: {
  icon: React.ElementType;
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4 border-b border-terminal-border pb-3">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
          <Icon className="h-4 w-4 text-terminal-accent" />
        </div>
        <div className="min-w-0">
          <h2 className="font-mono text-sm font-semibold uppercase tracking-widest text-terminal-text">
            {title}
          </h2>
          <p className="truncate font-mono text-[10px] text-terminal-muted">
            {subtitle}
          </p>
        </div>
      </div>
      {action}
    </div>
  );
}

function Metric({
  index,
  label,
  value,
  detail,
  tone = "default",
}: {
  index: string;
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "positive";
}) {
  return (
    <div className="group relative overflow-hidden rounded border border-terminal-border bg-terminal-surface px-4 py-4 transition-colors hover:border-terminal-accent/30">
      <div className="absolute right-3 top-2 font-display text-3xl font-bold text-terminal-border/50">
        {index}
      </div>
      <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-terminal-muted">
        {label}
      </p>
      <p
        className={clsx(
          "mt-3 font-mono text-xl font-semibold tracking-tight",
          tone === "positive" ? "text-terminal-green" : "text-terminal-text"
        )}
      >
        {value}
      </p>
      <p className="mt-1 font-mono text-[9px] text-terminal-muted">{detail}</p>
      <div className="absolute bottom-0 left-0 h-px w-0 bg-terminal-accent transition-all duration-300 group-hover:w-full" />
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-[1600px]">
      <header className="mb-6 flex flex-col justify-between gap-4 border-b border-terminal-border pb-5 sm:flex-row sm:items-end">
        <div>
          <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-terminal-muted">
            <span>Console</span>
            <ChevronRight className="h-3 w-3" />
            <span className="text-terminal-accent">Overview</span>
          </div>
          <h1 className="font-display text-xl font-bold uppercase tracking-[0.16em] text-terminal-text sm:text-2xl">
            Market Command
          </h1>
          <p className="mt-1 max-w-xl font-mono text-xs text-terminal-muted">
            Portfolio telemetry, tracked assets and AI research operations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-[9px] uppercase tracking-widest text-terminal-muted">
            Snapshot / Demo data
          </span>
          <span className="inline-flex items-center gap-1.5 rounded border border-terminal-green/20 bg-terminal-green/5 px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-terminal-green">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-green" />
            Market open
          </span>
        </div>
      </header>

      <section className="mb-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          index="01"
          label="Net worth"
          value={formatCurrency(portfolio.netWorth)}
          detail="Cash + current market value"
        />
        <Metric
          index="02"
          label="Market value"
          value={formatCurrency(portfolio.marketValue)}
          detail="4 positions currently open"
        />
        <Metric
          index="03"
          label="Buying power"
          value={formatCurrency(portfolio.buyingPower)}
          detail="69.5% available capital"
        />
        <Metric
          index="04"
          label="Unrealized P/L"
          value={`+${formatCurrency(portfolio.pnl)}`}
          detail={`+${portfolio.returnPct.toFixed(2)}% total return`}
          tone="positive"
        />
      </section>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="space-y-6 xl:col-span-8">
          <section>
            <SectionHeader
              icon={LineChart}
              title="Tracked Market"
              subtitle="Priority assets and latest price movement"
              action={
                <Link
                  href="/dashboard/portfolio"
                  className="flex items-center gap-1.5 rounded border border-terminal-border px-2 py-1.5 font-mono text-[9px] uppercase tracking-wider text-terminal-muted transition-colors hover:border-terminal-accent/40 hover:text-terminal-accent"
                >
                  Portfolio
                  <ArrowRight className="h-3 w-3" />
                </Link>
              }
            />
            <div className="overflow-hidden rounded border border-terminal-border bg-terminal-surface">
              <div className="grid grid-cols-[1fr_auto_auto] gap-4 border-b border-terminal-border bg-terminal-bg px-3 py-2">
                {["Asset", "Last price", "24h"].map((label, index) => (
                  <span
                    key={label}
                    className={clsx(
                      "font-mono text-[9px] uppercase tracking-wider text-terminal-muted",
                      index > 0 && "text-right"
                    )}
                  >
                    {label}
                  </span>
                ))}
              </div>
              {watchlist.map((stock) => (
                <div
                  key={stock.symbol}
                  className="grid grid-cols-[1fr_auto_auto] items-center gap-4 border-b border-terminal-border px-3 py-3 transition-colors last:border-0 hover:bg-terminal-accent/[0.035]"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-terminal-accent/25 bg-terminal-accent/5 font-display text-[10px] font-bold text-terminal-accent">
                      {stock.symbol.slice(0, 2)}
                    </span>
                    <div>
                      <p className="font-mono text-xs font-bold tracking-wider text-terminal-text">
                        {stock.symbol}
                      </p>
                      <p className="font-mono text-[9px] text-terminal-muted">{stock.name}</p>
                    </div>
                  </div>
                  <span className="font-mono text-xs text-terminal-text">
                    {formatCurrency(stock.price)}
                  </span>
                  <span
                    className={clsx(
                      "flex w-16 items-center justify-end gap-1 font-mono text-[10px]",
                      stock.change >= 0 ? "text-terminal-green" : "text-terminal-red"
                    )}
                  >
                    {stock.change >= 0 ? (
                      <ArrowUpRight className="h-3 w-3" />
                    ) : (
                      <ArrowDownRight className="h-3 w-3" />
                    )}
                    {stock.change >= 0 ? "+" : ""}
                    {stock.change.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section>
            <SectionHeader
              icon={Activity}
              title="Capital Allocation"
              subtitle="Current concentration across open positions"
            />
            <div className="grid gap-x-6 gap-y-4 sm:grid-cols-2">
              {allocation.map((item) => (
                <div key={item.symbol}>
                  <div className="mb-1.5 flex items-end justify-between">
                    <div>
                      <span className="font-mono text-[10px] font-semibold text-terminal-text">
                        {item.symbol}
                      </span>
                      <span className="ml-2 font-mono text-[9px] text-terminal-muted">
                        {formatCurrency(item.value)}
                      </span>
                    </div>
                    <span className="font-mono text-[10px] text-terminal-text">
                      {item.percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-1 overflow-hidden rounded-full bg-terminal-border">
                    <div
                      className="h-full rounded-full bg-terminal-accent"
                      style={{ width: `${item.percent}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <aside className="space-y-6 xl:col-span-4">
          <section>
            <SectionHeader
              icon={Radio}
              title="System Pulse"
              subtitle="Services and data availability"
            />
            <div className="space-y-1">
              {[
                { icon: Database, label: "Market data", value: "Connected", tone: "text-terminal-green" },
                { icon: Bot, label: "AI advisor", value: "Ready", tone: "text-terminal-green" },
                { icon: ShieldCheck, label: "Risk monitor", value: "Nominal", tone: "text-terminal-green" },
                { icon: CircleDollarSign, label: "Buying power", value: formatCurrency(portfolio.buyingPower), tone: "text-terminal-text" },
              ].map(({ icon: Icon, label, value, tone }) => (
                <div
                  key={label}
                  className="flex items-center justify-between rounded border border-terminal-border bg-terminal-surface px-3 py-2.5"
                >
                  <div className="flex items-center gap-2">
                    <Icon className="h-3.5 w-3.5 text-terminal-muted" />
                    <span className="font-mono text-[10px] text-terminal-muted">{label}</span>
                  </div>
                  <span className={clsx("font-mono text-[10px]", tone)}>{value}</span>
                </div>
              ))}
            </div>
          </section>

          <section>
            <SectionHeader
              icon={WalletCards}
              title="Quick Actions"
              subtitle="Continue a primary workflow"
            />
            <div className="space-y-2">
              {[
                {
                  href: "/dashboard/portfolio",
                  icon: BriefcaseBusiness,
                  title: "Inspect portfolio",
                  detail: "Positions, allocation and returns",
                },
                {
                  href: "/dashboard/advisor",
                  icon: Bot,
                  title: "Ask AI advisor",
                  detail: "Run research against your thesis",
                },
                {
                  href: "/dashboard/sandbox",
                  icon: FlaskConical,
                  title: "Open sandbox",
                  detail: "Test a trade without capital risk",
                },
              ].map(({ href, icon: Icon, title, detail }) => (
                <Link
                  key={href}
                  href={href}
                  className="group flex items-center gap-3 rounded border border-terminal-border bg-terminal-surface px-3 py-3 transition-colors hover:border-terminal-accent/35 hover:bg-terminal-accent/[0.035]"
                >
                  <Icon className="h-4 w-4 text-terminal-accent" />
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-[10px] font-semibold uppercase tracking-wider text-terminal-text">
                      {title}
                    </p>
                    <p className="truncate font-mono text-[9px] text-terminal-muted">{detail}</p>
                  </div>
                  <ArrowRight className="h-3.5 w-3.5 text-terminal-muted transition-transform group-hover:translate-x-0.5 group-hover:text-terminal-accent" />
                </Link>
              ))}
            </div>
          </section>

          <div className="border-l border-terminal-accent/40 bg-terminal-accent/[0.035] px-3 py-3">
            <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-terminal-accent">
              Operator note
            </p>
            <p className="mt-1.5 font-mono text-[10px] leading-relaxed text-terminal-muted">
              Portfolio concentration is highest in MSFT at 31.4%. Review exposure before adding another technology position.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
