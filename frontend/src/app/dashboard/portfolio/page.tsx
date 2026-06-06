"use client";

import { useMemo, useState } from "react";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  BriefcaseBusiness,
  ChevronRight,
  CircleDollarSign,
  Eye,
  EyeOff,
  Search,
  WalletCards,
} from "lucide-react";
import { clsx } from "clsx";
import type { Holding } from "@/lib/types";

type PortfolioHolding = Holding & {
  companyName: string;
  currentPrice: number;
  dayChange: number;
  sector: string;
};

const mockHoldings: PortfolioHolding[] = [
  {
    symbol: "AAPL",
    companyName: "Apple Inc.",
    quantity: 10,
    avgPrice: 175.5,
    currentPrice: 192.35,
    dayChange: 1.42,
    sector: "Technology",
  },
  {
    symbol: "GOOGL",
    companyName: "Alphabet Inc.",
    quantity: 5,
    avgPrice: 140.2,
    currentPrice: 176.92,
    dayChange: -0.38,
    sector: "Communication",
  },
  {
    symbol: "MSFT",
    companyName: "Microsoft Corp.",
    quantity: 8,
    avgPrice: 388.75,
    currentPrice: 424.52,
    dayChange: 0.86,
    sector: "Technology",
  },
  {
    symbol: "NVDA",
    companyName: "NVIDIA Corp.",
    quantity: 12,
    avgPrice: 96.4,
    currentPrice: 118.11,
    dayChange: 2.17,
    sector: "Semiconductors",
  },
];

const virtualCash = 24_680;

function formatCurrency(value: number, hidden = false) {
  if (hidden) return "$ ••••••";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
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
  label,
  value,
  detail,
  tone = "default",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "positive" | "negative";
}) {
  return (
    <div className="border-l border-terminal-border pl-3 first:border-l-0 first:pl-0 sm:pl-4">
      <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-terminal-muted">
        {label}
      </p>
      <p
        className={clsx(
          "mt-1 font-mono text-base font-semibold tracking-tight sm:text-lg",
          tone === "default" && "text-terminal-text",
          tone === "positive" && "text-terminal-green",
          tone === "negative" && "text-terminal-red"
        )}
      >
        {value}
      </p>
      <p className="mt-0.5 font-mono text-[9px] text-terminal-muted">{detail}</p>
    </div>
  );
}

export default function PortfolioPage() {
  const [query, setQuery] = useState("");
  const [balancesHidden, setBalancesHidden] = useState(false);

  const metrics = useMemo(() => {
    const marketValue = mockHoldings.reduce(
      (sum, holding) => sum + holding.quantity * holding.currentPrice,
      0
    );
    const costBasis = mockHoldings.reduce(
      (sum, holding) => sum + holding.quantity * holding.avgPrice,
      0
    );
    const totalPnl = marketValue - costBasis;
    const largestPosition = mockHoldings.reduce((largest, holding) =>
      holding.quantity * holding.currentPrice >
      largest.quantity * largest.currentPrice
        ? holding
        : largest
    );

    return {
      marketValue,
      costBasis,
      totalPnl,
      totalReturn: (totalPnl / costBasis) * 100,
      netWorth: marketValue + virtualCash,
      largestPosition,
      largestAllocation:
        (largestPosition.quantity * largestPosition.currentPrice * 100) /
        marketValue,
    };
  }, []);

  const filteredHoldings = mockHoldings.filter((holding) => {
    const value = query.trim().toLowerCase();
    return (
      holding.symbol.toLowerCase().includes(value) ||
      holding.companyName.toLowerCase().includes(value)
    );
  });

  return (
    <div
      className="min-h-full bg-terminal-bg font-mono text-terminal-text"
      style={{
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
      }}
    >
      <header className="mb-6 flex flex-col justify-between gap-4 border-b border-terminal-border pb-5 sm:flex-row sm:items-end">
        <div>
          <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-terminal-muted">
            <span>Dashboard</span>
            <ChevronRight className="h-3 w-3" />
            <span className="text-terminal-accent">Portfolio</span>
          </div>
          <h1 className="font-display text-xl font-bold uppercase tracking-[0.16em] text-terminal-text">
            Capital Ledger
          </h1>
          <p className="mt-1 max-w-xl font-mono text-xs text-terminal-muted">
            Position-level exposure, cost basis and unrealized performance.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 rounded border border-terminal-green/20 bg-terminal-green/5 px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-terminal-green">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-green" />
            Market open
          </span>
          <button
            type="button"
            onClick={() => setBalancesHidden((current) => !current)}
            aria-label={balancesHidden ? "Show balances" : "Hide balances"}
            className="flex h-7 w-7 items-center justify-center rounded border border-terminal-border text-terminal-muted transition-colors hover:border-terminal-accent/40 hover:bg-terminal-accent/5 hover:text-terminal-accent"
          >
            {balancesHidden ? (
              <EyeOff className="h-3.5 w-3.5" />
            ) : (
              <Eye className="h-3.5 w-3.5" />
            )}
          </button>
        </div>
      </header>

      <section className="mb-6 grid grid-cols-2 gap-x-3 gap-y-5 border-b border-terminal-border pb-5 lg:grid-cols-4">
        <Metric
          label="Net worth"
          value={formatCurrency(metrics.netWorth, balancesHidden)}
          detail="Cash + market value"
        />
        <Metric
          label="Market value"
          value={formatCurrency(metrics.marketValue, balancesHidden)}
          detail={`${mockHoldings.length} open positions`}
        />
        <Metric
          label="Buying power"
          value={formatCurrency(virtualCash, balancesHidden)}
          detail="24.1% of net worth"
        />
        <Metric
          label="Unrealized P/L"
          value={
            balancesHidden
              ? "$ ••••••"
              : `${metrics.totalPnl >= 0 ? "+" : ""}${formatCurrency(metrics.totalPnl)}`
          }
          detail={formatPercent(metrics.totalReturn)}
          tone={metrics.totalPnl >= 0 ? "positive" : "negative"}
        />
      </section>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <section className="xl:col-span-8">
          <SectionHeader
            icon={BriefcaseBusiness}
            title="Open Positions"
            subtitle={`${filteredHoldings.length} of ${mockHoldings.length} positions visible`}
            action={
              <label className="relative block">
                <Search className="pointer-events-none absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-terminal-muted" />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="FILTER SYMBOL..."
                  className="h-7 w-36 rounded border border-terminal-border bg-terminal-bg pl-7 pr-2 font-mono text-[10px] uppercase text-terminal-text outline-none transition-colors placeholder:text-terminal-muted/50 focus:border-terminal-accent/50 sm:w-44"
                />
              </label>
            }
          />

          <div className="overflow-hidden rounded border border-terminal-border bg-terminal-surface">
            <div className="hidden grid-cols-[1.4fr_0.7fr_0.9fr_1fr_1fr] gap-3 border-b border-terminal-border bg-terminal-bg px-3 py-2 lg:grid">
              {["Asset", "Quantity", "Price", "Market value", "Return"].map(
                (label, index) => (
                  <span
                    key={label}
                    className={clsx(
                      "font-mono text-[9px] uppercase tracking-wider text-terminal-muted",
                      index > 0 && "text-right"
                    )}
                  >
                    {label}
                  </span>
                )
              )}
            </div>

            {filteredHoldings.length === 0 ? (
              <div className="px-4 py-12 text-center">
                <Search className="mx-auto mb-2 h-5 w-5 text-terminal-muted" />
                <p className="font-mono text-xs text-terminal-muted">
                  No position matches &quot;{query}&quot;.
                </p>
              </div>
            ) : (
              filteredHoldings.map((holding) => {
                const marketValue = holding.quantity * holding.currentPrice;
                const pnl =
                  (holding.currentPrice - holding.avgPrice) * holding.quantity;
                const returnPct =
                  ((holding.currentPrice - holding.avgPrice) / holding.avgPrice) *
                  100;
                const isPositive = pnl >= 0;

                return (
                  <div
                    key={holding.symbol}
                    className="group grid grid-cols-2 gap-3 border-b border-terminal-border px-3 py-3 transition-colors last:border-b-0 hover:bg-terminal-accent/[0.035] lg:grid-cols-[1.4fr_0.7fr_0.9fr_1fr_1fr] lg:items-center"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-terminal-accent/25 bg-terminal-accent/5 font-display text-[10px] font-bold text-terminal-accent">
                        {holding.symbol.slice(0, 2)}
                      </div>
                      <div className="min-w-0">
                        <p className="font-mono text-xs font-bold tracking-wider text-terminal-text">
                          {holding.symbol}
                        </p>
                        <p className="truncate font-mono text-[9px] text-terminal-muted">
                          {holding.companyName}
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="font-mono text-xs text-terminal-text">
                        {holding.quantity}
                      </p>
                      <p className="font-mono text-[9px] text-terminal-muted lg:hidden">
                        SHARES
                      </p>
                    </div>

                    <div>
                      <p className="font-mono text-[9px] uppercase text-terminal-muted lg:hidden">
                        Last price
                      </p>
                      <p className="font-mono text-xs text-terminal-text lg:text-right">
                        {formatCurrency(holding.currentPrice)}
                      </p>
                      <p
                        className={clsx(
                          "flex items-center gap-1 font-mono text-[9px] lg:justify-end",
                          holding.dayChange >= 0
                            ? "text-terminal-green"
                            : "text-terminal-red"
                        )}
                      >
                        {holding.dayChange >= 0 ? (
                          <ArrowUpRight className="h-2.5 w-2.5" />
                        ) : (
                          <ArrowDownRight className="h-2.5 w-2.5" />
                        )}
                        {formatPercent(holding.dayChange)}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="font-mono text-[9px] uppercase text-terminal-muted lg:hidden">
                        Market value
                      </p>
                      <p className="font-mono text-xs font-medium text-terminal-text">
                        {formatCurrency(marketValue, balancesHidden)}
                      </p>
                      <p className="font-mono text-[9px] text-terminal-muted">
                        AVG {formatCurrency(holding.avgPrice)}
                      </p>
                    </div>

                    <div className="col-span-2 flex items-center justify-between border-t border-terminal-border/70 pt-2 lg:col-span-1 lg:block lg:border-0 lg:pt-0 lg:text-right">
                      <p
                        className={clsx(
                          "font-mono text-xs font-semibold",
                          isPositive
                            ? "text-terminal-green"
                            : "text-terminal-red"
                        )}
                      >
                        {balancesHidden
                          ? "$ ••••••"
                          : `${isPositive ? "+" : ""}${formatCurrency(pnl)}`}
                      </p>
                      <p
                        className={clsx(
                          "font-mono text-[9px]",
                          isPositive
                            ? "text-terminal-green/70"
                            : "text-terminal-red/70"
                        )}
                      >
                        {formatPercent(returnPct)}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>

        <aside className="space-y-6 xl:col-span-4">
          <section>
            <SectionHeader
              icon={BarChart3}
              title="Allocation"
              subtitle="Exposure by open position"
            />
            <div className="space-y-3">
              {mockHoldings
                .slice()
                .sort(
                  (a, b) =>
                    b.quantity * b.currentPrice - a.quantity * a.currentPrice
                )
                .map((holding) => {
                  const value = holding.quantity * holding.currentPrice;
                  const allocation = (value / metrics.marketValue) * 100;

                  return (
                    <div key={holding.symbol}>
                      <div className="mb-1.5 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] font-semibold text-terminal-text">
                            {holding.symbol}
                          </span>
                          <span className="font-mono text-[9px] text-terminal-muted">
                            {holding.sector}
                          </span>
                        </div>
                        <span className="font-mono text-[10px] text-terminal-text">
                          {allocation.toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-1 overflow-hidden rounded-full bg-terminal-border">
                        <div
                          className="h-full rounded-full bg-terminal-accent transition-[width] duration-700"
                          style={{ width: `${allocation}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          </section>

          <section>
            <SectionHeader
              icon={Activity}
              title="Portfolio Health"
              subtitle="Current account diagnostics"
            />
            <div className="space-y-1">
              {[
                {
                  icon: WalletCards,
                  label: "Cash reserve",
                  value: "Healthy",
                  tone: "text-terminal-green",
                },
                {
                  icon: CircleDollarSign,
                  label: "Cost basis",
                  value: formatCurrency(metrics.costBasis, balancesHidden),
                  tone: "text-terminal-text",
                },
                {
                  icon: BriefcaseBusiness,
                  label: "Largest position",
                  value: `${metrics.largestPosition.symbol} · ${metrics.largestAllocation.toFixed(1)}%`,
                  tone: "text-terminal-amber",
                },
              ].map(({ icon: Icon, label, value, tone }) => (
                <div
                  key={label}
                  className="flex items-center justify-between rounded border border-terminal-border bg-terminal-surface px-3 py-2.5"
                >
                  <div className="flex items-center gap-2">
                    <Icon className="h-3.5 w-3.5 text-terminal-muted" />
                    <span className="font-mono text-[10px] text-terminal-muted">
                      {label}
                    </span>
                  </div>
                  <span className={clsx("font-mono text-[10px]", tone)}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}
