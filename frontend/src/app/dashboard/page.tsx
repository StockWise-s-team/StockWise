"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, Briefcase, TrendingUp } from "lucide-react";
import { useAuth } from "@/components/providers/AuthProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { marketApi, trackedSymbolsApi } from "@/lib/api";
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

const numberFormatter = new Intl.NumberFormat("vi-VN", {
  maximumFractionDigits: 2,
});

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, error: portfolioError } = usePortfolio(user?.id);
  const [trackedSymbols, setTrackedSymbols] = useState<string[]>([]);
  const [prices, setPrices] = useState<LatestPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboardData() {
      try {
        setLoading(true);
        setError(null);

        const symbols = await trackedSymbolsApi.list();
        if (cancelled) return;
        setTrackedSymbols(symbols);

        if (symbols.length > 0) {
          // Fetch latest price for all symbols in parallel
          const priceResults = await Promise.all(
            symbols.map((sym) =>
              marketApi.getLatestPrice(sym).catch(() => null)
            )
          );
          if (cancelled) return;
          setPrices(priceResults.filter((p): p is LatestPrice => p !== null));
        } else {
          setPrices([]);
        }
      } catch (err) {
        if (!cancelled) {
          setError("Unable to load tracked symbols. Please try again later.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDashboardData();

    return () => {
      cancelled = true;
    };
  }, []);

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
            icon={Activity}
            title="Tracked Markets"
            subtitle="Real-time watch list summary"
          />
          {user?.role === "ADMIN" && (
            <Link href="/dashboard/admin" passHref>
              <TerminalButton size="xs" tone="accent" className="mb-4">
                Manage Tracked Tickers
              </TerminalButton>
            </Link>
          )}
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
              { label: "PRICE", align: "right" },
              { label: "CHANGE", align: "right" },
              { label: "% CHANGE", align: "right" },
              { label: "VOLUME", align: "right" },
              { label: "ACTIONS", align: "right" },
            ]}
          >
            {prices.map((price) => {
              const isPositive = price.change >= 0;
              const textTone = isPositive ? "text-terminal-green" : "text-terminal-red";
              const sign = isPositive ? "+" : "";

              return (
                <tr
                  key={price.symbol}
                  className="border-b border-terminal-border hover:bg-terminal-surface/40 transition-colors"
                >
                  <td className="px-3 py-3 font-semibold text-terminal-accent">
                    <Link href={`/dashboard/market/${price.symbol}`} className="hover:underline">
                      {price.symbol}
                    </Link>
                  </td>
                  <td className="px-3 py-3 text-right font-medium">
                    {formatVnd(price.price)}
                  </td>
                  <td className={`px-3 py-3 text-right font-medium ${textTone}`}>
                    {sign}{numberFormatter.format(price.change)}
                  </td>
                  <td className={`px-3 py-3 text-right font-medium ${textTone}`}>
                    {sign}{numberFormatter.format(price.changePercent)}%
                  </td>
                  <td className="px-3 py-3 text-right text-terminal-muted">
                    {new Intl.NumberFormat("vi-VN").format(price.volume)}
                  </td>
                  <td className="px-3 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      <Link href={`/dashboard/market/${price.symbol}`}>
                        <TerminalButton size="xs" tone="muted">
                          Analyze
                        </TerminalButton>
                      </Link>
                      <Link href={`/dashboard/sandbox?symbol=${price.symbol}`}>
                        <TerminalButton size="xs" tone="accent">
                          Trade
                        </TerminalButton>
                      </Link>
                    </div>
                  </td>
                </tr>
              );
            })}
          </TerminalTable>
        )}
      </section>
    </div>
  );
}
