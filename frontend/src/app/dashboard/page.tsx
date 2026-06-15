"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Activity, Briefcase, Radio, RefreshCw, TrendingUp } from "lucide-react";
import { useAuth } from "@/components/providers/AuthProvider";
import { useMarketData, useMarketTicker } from "@/components/providers/MarketDataProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { marketApi, userSelectionsApi } from "@/lib/api";
import { formatVnd, formatPnl, pnlColor } from "@/lib/format";
import type { LatestPrice } from "@/lib/types";
import {
  TerminalMetricCard,
  TerminalNotice,
  TerminalSectionHeader,
  TerminalEmptyState,
  TerminalSkeletonRows,
  TerminalTable,
  TerminalButton,
} from "@/components/ui";
import { clsx } from "clsx";

const numberFormatter = new Intl.NumberFormat("vi-VN", {
  maximumFractionDigits: 2,
});

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, error: portfolioError } = usePortfolio(user?.id);
  const { connectionState } = useMarketData();
  const [trackedSymbols, setTrackedSymbols] = useState<string[]>([]);
  const [prices, setPrices] = useState<Record<string, LatestPrice>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshSymbols = useCallback(async (showLoading: boolean) => {
    try {
      if (showLoading) setLoading(true);
      setError(null);
      const symbols = await userSelectionsApi.listSymbols();
      setTrackedSymbols(symbols);

      if (symbols.length > 0) {
        try {
          const batch = await marketApi.getLatestPriceBatch(symbols);
          setPrices((prev) => ({ ...prev, ...(batch || {}) }));
        } catch {
          const settled = await Promise.allSettled(
            symbols.map((sym) => marketApi.getLatestPrice(sym))
          );
          const next: Record<string, LatestPrice> = {};
          settled.forEach((r, idx) => {
            if (r.status === "fulfilled" && r.value) {
              next[symbols[idx]] = r.value;
            }
          });
          setPrices((prev) => ({ ...prev, ...next }));
        }
      }
    } catch (err) {
      console.error("[Dashboard] Failed to refresh symbols", err);
      setError("Unable to load tracked symbols. Please try again later.");
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  // Initial load only — the layout-level MarketDataProvider handles the
  // 15s polling for symbol-list changes.
  useEffect(() => {
    void refreshSymbols(true);
  }, [refreshSymbols]);

  // Bridge: every live tick from MarketDataProvider should be reflected in
  // the row's price cell. We use a ref so the interval can read the latest
  // tick without re-rendering the whole list on every tick.
  const { getTicker } = useMarketData();
  const getTickerRef = useRef(getTicker);
  useEffect(() => {
    getTickerRef.current = getTicker;
  }, [getTicker]);
  useEffect(() => {
    const interval = setInterval(() => {
      setPrices((prev) => {
        let changed = false;
        const next = { ...prev };
        for (const sym of trackedSymbols) {
          const ticker = getTickerRef.current?.(sym) ?? null;
          if (ticker && ticker !== prev[sym]) {
            next[sym] = ticker;
            changed = true;
          }
        }
        return changed ? next : prev;
      });
    }, 500);
    return () => clearInterval(interval);
  }, [trackedSymbols]);

  return (
    <div className="min-h-full space-y-5 font-mono text-terminal-text">
      <header className="border-b border-terminal-border pb-4">
        <div className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-terminal-green animate-pulse" />
          System Active
        </div>
        <h1 className="font-display text-xl font-bold uppercase tracking-[0.18em] text-terminal-accent">
          Dashboard Overview
        </h1>
        <p className="mt-1 max-w-2xl text-xs leading-relaxed text-terminal-muted">
          Real-time portfolio valuation and watch list status. Select a ticker to analyze historical chart and business wiki.
        </p>
      </header>

      {(portfolioError || error) && (
        <TerminalNotice tone="danger">
          {portfolioError || error}
        </TerminalNotice>
      )}

      <section>
        <TerminalSectionHeader
          icon={Briefcase}
          title="Portfolio telemetry"
          subtitle="Current account valuation"
        />
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <TerminalMetricCard label="Total portfolio value" value={formatVnd(data?.totalValue)} />
          <TerminalMetricCard label="Virtual cash" value={formatVnd(data?.account.virtualCash)} />
          <TerminalMetricCard
            label="Unrealized P/L"
            value={<span className={pnlColor(data?.unrealizedPnl)}>{formatPnl(data?.unrealizedPnl)}</span>}
          />
          <TerminalMetricCard
            label="Realized P/L"
            value={<span className={pnlColor(data?.realizedPnl)}>{formatPnl(data?.realizedPnl)}</span>}
          />
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between">
          <TerminalSectionHeader
            icon={Radio}
            title="Tracked Markets"
            subtitle="Real-time watch list summary"
            action={<ConnectionBadge state={connectionState} />}
          />
          <div className="mb-4 flex items-center gap-2">
            <button
              type="button"
              onClick={() => void refreshSymbols(false)}
              className="inline-flex items-center gap-1 rounded border border-terminal-border bg-terminal-surface px-2 py-1 text-[10px] font-mono font-semibold uppercase tracking-wider text-terminal-muted hover:border-terminal-accent/30 hover:text-terminal-text"
              title="Refresh watch list"
            >
              <RefreshCw className="h-3 w-3" />
              Refresh
            </button>
            {user?.role === "ADMIN" && (
              <Link href="/dashboard/admin" passHref>
                <TerminalButton size="xs" tone="accent">
                  Manage Tracked Tickers
                </TerminalButton>
              </Link>
            )}
          </div>
        </div>

        {loading ? (
          <TerminalSkeletonRows rows={4} />
        ) : trackedSymbols.length === 0 ? (
          <TerminalEmptyState
            icon={TrendingUp}
            title="No symbols are currently tracked"
            description="Go to the Admin Console to track stock tickers and initialize their market prices."
          />
        ) : (
          <TerminalTable
            headers={[
              { label: "SYMBOL" },
              { label: "OPEN", align: "right" },
              { label: "HIGH", align: "right" },
              { label: "LOW", align: "right" },
              { label: "CLOSE", align: "right" },
              { label: "CHANGE", align: "right" },
              { label: "% CHANGE", align: "right" },
              { label: "VOLUME", align: "right" },
              { label: "ACTIONS", align: "right" },
            ]}
          >
            {trackedSymbols.map((sym) => (
              <WatchRow key={sym} symbol={sym} />
            ))}
          </TerminalTable>
        )}
      </section>
    </div>
  );
}

function ConnectionBadge({ state }: { state: string }) {
  if (state === "connected") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded border border-terminal-green/30 bg-terminal-green/5 px-2 py-0.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-terminal-green">
        <span className="relative inline-flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-terminal-green opacity-60" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-terminal-green" />
        </span>
        Live
      </span>
    );
  }
  if (state === "connecting" || state === "reconnecting") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded border border-terminal-amber/30 bg-terminal-amber/5 px-2 py-0.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-terminal-amber">
        <span className="h-2 w-2 animate-pulse rounded-full bg-terminal-amber" />
        Connecting
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 rounded border border-terminal-border bg-terminal-surface px-2 py-0.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-terminal-muted">
      <Activity className="h-3 w-3" />
      {state === "error" ? "Error" : "Idle"}
    </span>
  );
}

function WatchRow({ symbol }: { symbol: string }) {
  const { ticker, tickCount, connectionState } = useMarketTicker(symbol);
  const { user } = useAuth();
  const price = ticker;
  const isLive = connectionState === "connected";

  if (!price) {
    return (
      <tr
        key={symbol}
        className="border-b border-terminal-border hover:bg-terminal-surface/40 transition-colors"
      >
        <td className="px-3 py-3 font-semibold text-terminal-accent">
          <Link href={`/dashboard/market/${symbol}`} className="hover:underline">
            {symbol}
          </Link>
        </td>
        <td colSpan={8} className="px-3 py-3 text-right text-terminal-muted text-[10px]">
          awaiting live tick…
        </td>
      </tr>
    );
  }

  const isPositive = price.change >= 0;
  const textTone = isPositive ? "text-terminal-green" : "text-terminal-red";
  const sign = isPositive ? "+" : "";

  return (
    <tr
      key={`${symbol}-${tickCount}`}
      className={clsx(
        "border-b border-terminal-border hover:bg-terminal-surface/40 transition-colors",
        isLive && tickCount > 0 && "animate-[pulse_2s_ease-in-out_1]"
      )}
    >
      <td className="px-3 py-3 font-semibold text-terminal-accent">
        <Link href={`/dashboard/market/${symbol}`} className="hover:underline">
          {symbol}
        </Link>
        {tickCount > 0 && (
          <span className="ml-1 text-[9px] text-terminal-green">⚡{tickCount}</span>
        )}
      </td>
      <td className="px-3 py-3 text-right font-medium">{formatVnd(price.open)}</td>
      <td className="px-3 py-3 text-right font-medium">{formatVnd(price.high)}</td>
      <td className="px-3 py-3 text-right font-medium">{formatVnd(price.low)}</td>
      <td className="px-3 py-3 text-right font-medium">{formatVnd(price.close)}</td>
      <td className={`px-3 py-3 text-right font-medium ${textTone}`}>
        {sign}
        {numberFormatter.format(price.change)}
      </td>
      <td className={`px-3 py-3 text-right font-medium ${textTone}`}>
        {sign}
        {numberFormatter.format(price.changePercent)}%
      </td>
      <td className="px-3 py-3 text-right text-terminal-muted">
        {new Intl.NumberFormat("vi-VN").format(price.volume)}
      </td>
      <td className="px-3 py-3 text-right">
        <div className="flex justify-end gap-2">
          <Link href={`/dashboard/market/${symbol}`}>
            <TerminalButton size="xs" tone="muted">
              Analyze
            </TerminalButton>
          </Link>
          <Link href={`/dashboard/sandbox?symbol=${symbol}`}>
            <TerminalButton size="xs" tone="accent">
              Trade
            </TerminalButton>
          </Link>
        </div>
      </td>
    </tr>
  );
}

